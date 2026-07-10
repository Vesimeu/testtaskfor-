from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka, inject
from fastapi import APIRouter, File, Form, HTTPException, Path, UploadFile, status
from fastapi.responses import FileResponse

from src.api.dto.file_dto import FileResponseDTO, FileUpdateDTO
from src.core.config import settings
from src.services.file_service import FileService
from src.tasks.tasks import process_file

router = APIRouter(
    prefix="/files",
    tags=["files"],
    route_class=DishkaRoute,
)


@router.get("", response_model=list[FileResponseDTO])
@inject
async def list_files(
    service: FromDishka[FileService],
) -> list[FileResponseDTO]:
    """
    Получение списка всех загруженных файлов.

    Возвращает:
    - **list[FileResponseDTO]**: Список объектов файлов с их метаданными.
    """
    return await service.list_files()


@router.post("", response_model=FileResponseDTO, status_code=status.HTTP_201_CREATED)
@inject
async def create_file(
    service: FromDishka[FileService],
    title: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
) -> FileResponseDTO:
    """
    Загрузка нового файла в хранилище и создание записи в БД.
    После успешной загрузки инициируется фоновая задача анализа файла.

    Параметры:
    - **title** (str): Название файла, заданное пользователем.
    - **file** (UploadFile): Загружаемый файл.

    Возвращает:
    - **FileResponseDTO**: Созданный объект файла.
    """
    file_item = await service.create_file(title=title, upload_file=file)
    process_file.delay(file_item.id)
    return file_item


@router.get("/{file_id}", response_model=FileResponseDTO)
@inject
async def get_file(
    file_id: Annotated[str, Path(description="Идентификатор файла (UUID)")],
    service: FromDishka[FileService],
) -> FileResponseDTO:
    """
    Получение детальной информации о файле по его идентификатору.

    Параметры:
    - **file_id** (str): Идентификатор файла.

    Возвращает:
    - **FileResponseDTO**: Объект файла.
    """
    return await service.get_file(file_id)


@router.patch("/{file_id}", response_model=FileResponseDTO)
@inject
async def update_file(
    file_id: Annotated[str, Path(description="Идентификатор файла (UUID)")],
    payload: FileUpdateDTO,
    service: FromDishka[FileService],
) -> FileResponseDTO:
    """
    Обновление названия файла.

    Параметры:
    - **file_id** (str): Идентификатор файла.
    - **payload** (FileUpdateDTO): Объект с новым названием.

    Возвращает:
    - **FileResponseDTO**: Обновленный объект файла.
    """
    return await service.update_file(file_id=file_id, title=payload.title)


@router.get("/{file_id}/download")
@inject
async def download_file(
    file_id: Annotated[str, Path(description="Идентификатор файла (UUID)")],
    service: FromDishka[FileService],
) -> FileResponse:
    """
    Скачивание содержимого файла.

    Параметры:
    - **file_id** (str): Идентификатор файла.

    Возвращает:
    - **FileResponse**: Поток содержимого файла для скачивания браузером.
    """
    file_item = await service.get_file(file_id)
    stored_path = settings.STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored file not found on disk",
        )
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_file(
    file_id: Annotated[str, Path(description="Идентификатор файла (UUID)")],
    service: FromDishka[FileService],
) -> None:
    """
    Удаление файла из БД и физического хранилища.

    Параметры:
    - **file_id** (str): Идентификатор файла.
    """
    await service.delete_file(file_id)
