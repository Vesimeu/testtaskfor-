from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertResponseDTO(BaseModel):
    """DTO ответа с данными алерта."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Уникальный идентификатор алерта.")
    file_id: str = Field(description="Идентификатор связанного файла.")
    level: str = Field(description="Уровень важности (info, warning, critical).")
    message: str = Field(description="Содержимое сообщения об алерте.")
    created_at: datetime = Field(description="Дата и время генерации алерта.")
