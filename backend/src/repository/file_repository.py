from dishka import Provider, Scope, provide
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.stored_file import StoredFile
from src.repository.base_repository import BaseRepository


class FileRepository(BaseRepository[StoredFile]):
    """
    Репозиторий для сущности StoredFile.
    Решает задачу прямого чтения и записи метаданных файлов в базу данных.
    Используется в FileService для управления файлами.
    """

    def __init__(self) -> None:
        super().__init__(StoredFile)

    async def get_all_ordered(self, session: AsyncSession) -> list[StoredFile]:
        """
        Получить все файлы, отсортированные по времени создания (сначала новые).

        Параметры:
        - **session** (AsyncSession): Сессия БД.

        Возвращает:
        - **list[StoredFile]**: Список файлов.
        """
        stmt = select(self.model).order_by(self.model.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())


class FileRepoProvider(Provider):
    """Провайдер Dishka для инъекции FileRepository."""
    scope = Scope.REQUEST

    @provide
    def file_repository(self) -> FileRepository:
        return FileRepository()
