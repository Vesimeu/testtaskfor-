from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# Асинхронное подключение для FastAPI HTTP-слоя
async_engine = create_async_engine(settings.database_url_async)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

# Синхронное подключение для Celery-воркера
sync_engine = create_engine(settings.database_url_sync)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
