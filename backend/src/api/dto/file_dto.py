from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FileResponseDTO(BaseModel):
    """DTO ответа с данными файла."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Уникальный идентификатор файла (UUID).")
    title: str = Field(description="Пользовательское название файла.")
    original_name: str = Field(description="Исходное имя загруженного файла.")
    mime_type: str = Field(description="MIME-тип файла.")
    size: int = Field(description="Размер файла в байтах.")
    processing_status: str = Field(description="Статус обработки (uploaded, processing, processed, failed).")
    scan_status: str | None = Field(default=None, description="Результат сканирования (clean, suspicious, failed).")
    scan_details: str | None = Field(default=None, description="Детали сканирования / обнаруженные угрозы.")
    metadata_json: dict | None = Field(default=None, description="Извлеченные метаданные (для текста или PDF).")
    requires_attention: bool = Field(description="Флаг необходимости внимания со стороны администратора.")
    created_at: datetime = Field(description="Дата и время загрузки файла.")
    updated_at: datetime = Field(description="Дата и время последнего обновления файла.")


class FileUpdateDTO(BaseModel):
    """DTO для обновления названия файла."""
    title: str = Field(min_length=1, max_length=255, description="Новое название файла.")
