import asyncio
import logging
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app import create_app
from src.core.config import settings

# Настройка логирования для тестов
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)
_CLEANED = False


def _cleanup_db_schema() -> None:
    """Полная очистка тестовой БД."""
    global _CLEANED
    if _CLEANED:
        return
    try:
        cleanup_engine = create_async_engine(settings.database_url_async_test, future=True)

        async def _drop_public_schema():
            async with cleanup_engine.begin() as conn:
                await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
                await conn.execute(text("CREATE SCHEMA public;"))

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_drop_public_schema())
            loop.run_until_complete(cleanup_engine.dispose())
        finally:
            loop.close()
    except Exception as exc:
        _LOGGER.error("Cleanup DB schema failed: %s", exc)
    finally:
        _CLEANED = True


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Перед стартом тестов применяем миграции, после — откатываем."""
    project_root = Path(__file__).parent.parent
    alembic_ini_path = project_root / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    
    # Подменяем URL подключения в alembic.ini на тестовый
    alembic_cfg.set_main_option("test.url", settings.database_url_async_test)
    
    command.upgrade(alembic_cfg, "head")
    try:
        yield
    finally:
        _cleanup_db_schema()


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Асинхронный движок для тестовой БД."""
    engine = create_async_engine(settings.database_url_async_test, future=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="function")
async def connection(engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    """Транзакционное соединение с автоматическим откатом."""
    conn = await engine.connect()
    tx = await conn.begin()
    try:
        yield conn
    finally:
        await tx.rollback()
        await conn.close()


@pytest.fixture(scope="function")
async def session_factory(connection: AsyncConnection):
    """Синхронизированная фабрика сессий."""
    return async_sessionmaker(bind=connection, expire_on_commit=False, autoflush=False)


@pytest.fixture(scope="function")
async def app(session_factory) -> FastAPI:
    """Создает инстанс FastAPI с переопределенной тестовой Dishka-сессией."""
    from src.core.container import AppProvider
    from src.core.container import providers as app_providers
    from dishka import Provider, Scope, provide

    app = create_app()

    class TestAppProvider(AppProvider):
        @provide(scope=Scope.REQUEST)
        async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
            async with session_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

    # Заменяем оригинальный AppProvider на TestAppProvider
    test_providers = []
    for p in app_providers:
        if isinstance(p, AppProvider):
            test_providers.append(TestAppProvider())
        else:
            test_providers.append(p)

    container = make_async_container(*test_providers)
    setup_dishka(container, app)
    return app


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный клиент HTTPX для интеграционных тестов API."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для получения сессии базы данных в тестах."""
    async with session_factory() as session:
        yield session

