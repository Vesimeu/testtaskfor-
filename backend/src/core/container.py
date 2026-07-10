from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import async_session_maker
from src.repository.alert_repository import AlertRepoProvider
from src.repository.file_repository import FileRepoProvider
from src.services.alert_service import AlertServiceProvider
from src.services.file_service import FileServiceProvider


class AppProvider(Provider):
    """
    Главный провайдер зависимостей приложения.
    Решает задачу открытия и закрытия транзакционных сессий базы данных.
    Используется Dishka при каждом входящем HTTP запросе.
    """

    @provide(scope=Scope.REQUEST)
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Генератор сессии БД с автоматическим управлением транзакциями."""
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


providers = [
    AppProvider(),
    FileRepoProvider(),
    AlertRepoProvider(),
    FileServiceProvider(),
    AlertServiceProvider(),
]


def create_async_container() -> AsyncContainer:
    """Создать и вернуть асинхронный DI-контейнер Dishka."""
    return make_async_container(*providers)
