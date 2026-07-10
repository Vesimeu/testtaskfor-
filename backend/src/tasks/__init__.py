from src.tasks.celery_app import celery_app
from src.tasks.tasks import process_file

__all__ = ["celery_app", "process_file"]
