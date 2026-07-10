import io
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.models.stored_file import StoredFile


@pytest.fixture(autouse=True)
def mock_celery_delay():
    """Автоматически подменяет вызов Celery-задач для тестов."""
    with patch("src.tasks.tasks.process_file.delay") as mock:
        yield mock


@pytest.mark.anyio
async def test_list_files_empty(client: AsyncClient):
    """Проверяет получение пустого списка файлов на старте."""
    response = await client.get("/files")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_upload_file(client: AsyncClient, session: AsyncSession, mock_celery_delay):
    """Проверяет загрузку файла через API и корректность записи в БД."""
    file_content = b"fake file content line 1\nline 2"
    file_data = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    data = {"title": "Test File Title"}

    response = await client.post("/files", data=data, files=file_data)
    assert response.status_code == 201
    
    res_data = response.json()
    assert res_data["original_name"] == "test.txt"
    assert res_data["title"] == "Test File Title"
    assert res_data["size"] == len(file_content)
    assert res_data["processing_status"] == "uploaded"
    
    file_id = res_data["id"]

    # Проверяем, что запись действительно появилась в БД
    stmt = select(StoredFile).where(StoredFile.id == file_id)
    db_result = await session.execute(stmt)
    db_file = db_result.scalar_one_or_none()
    assert db_file is not None
    assert db_file.title == "Test File Title"

    # Проверяем, что была инициирована Celery-задача с ID файла
    mock_celery_delay.assert_called_once_with(file_id)


@pytest.mark.anyio
async def test_delete_file_cascade(client: AsyncClient, session: AsyncSession):
    """Проверяет успешность каскадного удаления алертов при удалении файла."""
    # 1. Вручную создаем файл и связанный с ним алерт
    db_file = StoredFile(
        id="739e5f96-f87d-4fca-9e5a-e865a097d0c3",
        original_name="malicious.exe",
        stored_name="739e5f96-f87d-4fca-9e5a-e865a097d0c3.exe",
        mime_type="application/octet-stream",
        title="Malicious file",
        size=1024,
        processing_status="failed",
    )
    session.add(db_file)
    await session.flush()

    db_alert = Alert(
        file_id=db_file.id,
        level="high",
        message="Suspicious threat detected in file",
    )
    session.add(db_alert)
    await session.commit()

    # 2. Вызываем API удаления файла
    delete_response = await client.delete(f"/files/{db_file.id}")
    assert delete_response.status_code == 204

    # 3. Убеждаемся, что сессия очищена и база данных пуста
    db_file_stmt = select(StoredFile).where(StoredFile.id == db_file.id)
    db_file_res = await session.execute(db_file_stmt)
    assert db_file_res.scalar_one_or_none() is None

    db_alert_stmt = select(Alert).where(Alert.file_id == db_file.id)
    db_alert_res = await session.execute(db_alert_stmt)
    assert db_alert_res.scalar_one_or_none() is None
