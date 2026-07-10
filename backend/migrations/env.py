import asyncio
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.core.config import settings
from src.models import Base

# Инициализируем логгер
logger = logging.getLogger("alembic.runtime.migration")

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata
target_metadata = Base.metadata

# Устанавливаем дефолтный URL из настроек
if settings.database_url_async:
    config.set_main_option("sqlalchemy.url", settings.database_url_async)


def run_migrations_offline() -> None:
    """Запуск миграций в offline режиме."""
    url = config.get_main_option("test.url")
    if not url:
        url = config.get_main_option("sqlalchemy.url")
        
    logger.info(f"Database URL (offline): {url}")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Запуск миграций в асинхронном режиме."""
    test_url = config.get_main_option("test.url")
    if test_url:
        logger.info(f"Database URL (test online): {test_url}")
        connectable = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="test.",
            poolclass=pool.NullPool,
        )
    else:
        logger.info(f"Database URL (online): {settings.database_url_async}")
        connectable = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в online режиме."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
