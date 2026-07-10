from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.core.container import create_async_container


from src.core.config import settings


def create_app() -> FastAPI:
    """
    Создание и конфигурация FastAPI приложения.
    Инициализирует маршруты, CORS политики и DI-контейнер Dishka.
    """
    app = FastAPI(title="File Exchange MVP")

    #TODO Предусмотреть этот факт при деплое приложения
    origins = settings.CORS_ORIGINS_DEV + settings.CORS_ORIGINS_PROD
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    container = create_async_container()
    setup_dishka(container=container, app=app)

    return app


app = create_app()
