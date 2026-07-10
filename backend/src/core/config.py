import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Класс конфигурации приложения.
    Решает задачу централизованного хранения настроек окружения и путей проекта.
    Используется во всех слоях приложения, включая сервисы, воркер и БД.
    """
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage" / "files"

    #Хардор намеренный
    DB_URL: str = os.environ.get(
        "DB_URL", "postgresql+asyncpg://postgres:123123@localhost:5432/testsvo"
    )
    TEST_DB_URL: str = os.environ.get(
        "TEST_DB_URL", "postgresql+asyncpg://postgres:123123@localhost:5432/svo"
    )

    @property
    def database_url_async(self) -> str:
        return self.DB_URL

    @property
    def database_url_sync(self) -> str:
        return self.DB_URL.replace("postgresql+asyncpg://", "postgresql://")

    @property
    def database_url_async_test(self) -> str:
        return self.TEST_DB_URL

    @property
    def database_url_sync_test(self) -> str:
        return self.TEST_DB_URL.replace("postgresql+asyncpg://", "postgresql://")


    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://backend-redis:6379/0")

    CORS_ORIGINS_DEV: list[str] = [
        x.strip() for x in os.environ.get(
            "CORS_ORIGINS_DEV", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",") if x.strip()
    ]
    CORS_ORIGINS_PROD: list[str] = [
        x.strip() for x in os.environ.get(
            "CORS_ORIGINS_PROD", ""
        ).split(",") if x.strip()
    ]


settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
