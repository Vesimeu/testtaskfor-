import os
from pathlib import Path


class Settings:
    """
    Класс конфигурации приложения.
    Решает задачу централизованного хранения настроек окружения и путей проекта.
    Используется во всех слоях приложения, включая сервисы, воркер и БД.
    """
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage" / "files"

    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.environ.get("PGPORT", "5432")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "test")

    @property
    def database_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://backend-redis:6379/0")


settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
