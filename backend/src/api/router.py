from fastapi import APIRouter

from src.api.routers import alerts_router, files_router

api_router = APIRouter()

api_router.include_router(files_router.router)
api_router.include_router(alerts_router.router)
