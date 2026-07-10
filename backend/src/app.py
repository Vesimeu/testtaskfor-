from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.core.container import create_async_container


def create_app() -> FastAPI:
    """
    Создание и конфигурация FastAPI приложения.
    Инициализирует маршруты, CORS политики и DI-контейнер Dishka.
    """
    app = FastAPI(title="File Exchange MVP")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    container = create_async_container()
    setup_dishka(container=container, app=app)

    return app


app = create_app()
