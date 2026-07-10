from __future__ import annotations

from dishka.integrations.fastapi import DishkaRoute, FromDishka, inject
from fastapi import APIRouter

from src.api.dto.alert_dto import AlertResponseDTO
from src.services.alert_service import AlertService

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    route_class=DishkaRoute,
)


@router.get("", response_model=list[AlertResponseDTO])
@inject
async def list_alerts(
    service: FromDishka[AlertService],
) -> list[AlertResponseDTO]:
    """
    Получение списка всех алертов безопасности и обработки.

    Возвращает:
    - **list[AlertResponseDTO]**: Список объектов алертов.
    """
    return await service.list_alerts()
