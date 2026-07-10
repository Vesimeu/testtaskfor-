from dishka import Provider, Scope, provide
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.repository.base_repository import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """
    Репозиторий для сущности Alert.
    Решает задачу чтения и создания алертов безопасности в БД.
    Используется в AlertService и при выводе ленты алертов.
    """

    def __init__(self) -> None:
        super().__init__(Alert)

    async def get_all_ordered(self, session: AsyncSession) -> list[Alert]:
        """
        Получить все алерты, отсортированные по времени создания (сначала новые).

        Параметры:
        - **session** (AsyncSession): Сессия БД.

        Возвращает:
        - **list[Alert]**: Список алертов.
        """
        stmt = select(self.model).order_by(self.model.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())


class AlertRepoProvider(Provider):
    """Провайдер Dishka для инъекции AlertRepository."""
    scope = Scope.REQUEST

    @provide
    def alert_repository(self) -> AlertRepository:
        return AlertRepository()
