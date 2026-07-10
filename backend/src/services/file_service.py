import mimetypes
from pathlib import Path
from uuid import uuid4

from dishka import Provider, Scope, provide
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import NotFoundException
from src.models.stored_file import StoredFile
from src.repository.file_repository import FileRepository


class FileService:
    """
    Класс сервиса для управления файлами.

    Для чего нужен: решает бизнес-задачи загрузки новых файлов, переименования,
    удаления физических файлов с диска и получения информации о них.
    Где используется: в обработчиках HTTP API (files_router.py).
    """

    def __init__(self, session: AsyncSession, repo: FileRepository):
        self.session = session
        self.repo = repo

    async def get_file(self, file_id: str) -> StoredFile:
        """Получить файл по ID."""
        try:
            return await self.repo.get_by_id(self.session, file_id)
        except NotFoundException:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    async def list_files(self) -> list[StoredFile]:
        """Получить список всех файлов."""
        return await self.repo.get_all_ordered(self.session)

    async def create_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        """Создать запись файла и сохранить его на диск."""
        content = await upload_file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
        file_id = str(uuid4())
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"
        stored_path = settings.STORAGE_DIR / stored_name
        stored_path.write_bytes(content)
        mime_type = (
            upload_file.content_type
            or mimetypes.guess_type(stored_name)[0]
            or "application/octet-stream"
        )
        file_item = await self.repo.create(
            self.session,
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=mime_type,
            size=len(content),
            processing_status="uploaded",
        )
        return file_item

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        """Обновить метаданные файла."""
        file_item = await self.repo.update(self.session, file_id, title=title)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        return file_item

    async def delete_file(self, file_id: str) -> None:
        """Удалить запись файла из БД и физически с диска."""
        file_item = await self.repo.get_by_id(self.session, file_id, raise_if_not_found=False)
        if not file_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        stored_path = settings.STORAGE_DIR / file_item.stored_name
        if stored_path.exists():
            stored_path.unlink()
        await self.repo.delete(self.session, file_id)


class FileServiceProvider(Provider):
    """Провайдер Dishka для инъекции FileService."""
    scope = Scope.REQUEST

    @provide
    def file_service(self, session: AsyncSession, repo: FileRepository) -> FileService:
        return FileService(session, repo)
