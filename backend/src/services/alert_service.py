from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.repository.alert_repository import AlertRepository


class AlertService:
    """
    Класс сервиса для управления алертами.

    Для чего нужен: решает бизнес-задачи получения ленты алертов безопасности и
    создания новых уведомлений по файлам.
    Где используется: в обработчиках HTTP API (alerts_router.py).
    """

    def __init__(self, session: AsyncSession, repo: AlertRepository):
        self.session = session
        self.repo = repo

    async def list_alerts(self) -> list[Alert]:
        """Получить упорядоченный список алертов."""
        return await self.repo.get_all_ordered(self.session)

    async def create_alert(self, file_id: str, level: str, message: str) -> Alert:
        """Создать новый алерт для файла."""
        return await self.repo.create(
            self.session,
            file_id=file_id,
            level=level,
            message=message,
        )


class AlertServiceProvider(Provider):
    """Провайдер Dishka для инъекции AlertService."""
    scope = Scope.REQUEST

    @provide
    def alert_service(self, session: AsyncSession, repo: AlertRepository) -> AlertService:
        return AlertService(session, repo)
