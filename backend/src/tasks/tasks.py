from src.core.db import SyncSessionLocal
from src.services.file_processing_service import FileProcessingService
from src.tasks.celery_app import celery_app


@celery_app.task
def process_file(file_id: str) -> None:
    """
    Celery-задача для фонового анализа файла.
    Выполняет проверку расширения/размера, парсинг содержимого (PDF/текст) и запись алерта.
    Использует синхронную сессию БД для предотвращения проблем с event loop в Celery.
    """
    with SyncSessionLocal() as session:
        service = FileProcessingService(session)
        service.process_file(file_id)
