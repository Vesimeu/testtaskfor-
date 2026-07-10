from pathlib import Path

from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.alert import Alert
from src.models.stored_file import StoredFile


class FileProcessingService:
    """
    Класс сервиса для фоновой обработки файлов.

    Для чего нужен: решает бизнес-задачи последовательной проверки файлов на угрозы,
    потокового извлечения метаданных (количество страниц PDF, количество строк/символов текста)
    и автоматической генерации алертов безопасности в БД.
    Где используется: в Celery-воркере (tasks.py) внутри фоновых задач.
    """

    def __init__(self, session: Session):
        self.session = session

    def process_file(self, file_id: str) -> None:
        """
        Выполнить полную цепочку обработки файла: сканирование, метаданные и алерты.

        Параметры:
        - **file_id** (str): Идентификатор файла для обработки.
        """
        file_item = self.session.get(StoredFile, file_id)
        if not file_item:
            return
        file_item.processing_status = "processing"
        self.session.commit()
        try:
            reasons = self._scan_file(file_item)
            file_item.scan_status = "suspicious" if reasons else "clean"
            file_item.scan_details = ", ".join(reasons) if reasons else "no threats found"
            file_item.requires_attention = bool(reasons)
            stored_path = settings.STORAGE_DIR / file_item.stored_name
            if not stored_path.exists():
                file_item.processing_status = "failed"
                file_item.scan_status = file_item.scan_status or "failed"
                file_item.scan_details = "stored file not found during metadata extraction"
            else:
                metadata = {
                    "extension": Path(file_item.original_name).suffix.lower(),
                    "size_bytes": file_item.size,
                    "mime_type": file_item.mime_type,
                }
                if file_item.mime_type.startswith("text/"):
                    line_count, char_count = self._count_lines_and_chars(stored_path)
                    metadata["line_count"] = line_count
                    metadata["char_count"] = char_count
                elif file_item.mime_type == "application/pdf":
                    page_count = self._count_pdf_pages(stored_path)
                    metadata["approx_page_count"] = max(page_count, 1)
                file_item.metadata_json = metadata
                file_item.processing_status = "processed"
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            file_item.processing_status = "failed"
            file_item.scan_status = "failed"
            file_item.scan_details = f"Internal processing error: {str(exc)}"
            self.session.commit()
        finally:
            self._create_processing_alert(file_item)

    def _scan_file(self, file_item: StoredFile) -> list[str]:
        reasons: list[str] = []
        extension = Path(file_item.original_name).suffix.lower()
        if extension in {".exe", ".bat", ".cmd", ".sh", ".js"}:
            reasons.append(f"suspicious extension {extension}")
        if file_item.size > 10 * 1024 * 1024:
            reasons.append("file is larger than 10 MB")
        if extension == ".pdf" and file_item.mime_type not in {"application/pdf", "application/octet-stream"}:
            reasons.append("pdf extension does not match mime type")
        return reasons

    def _count_lines_and_chars(self, file_path: Path, chunk_size: int = 65536) -> tuple[int, int]:
        line_count = 0
        char_count = 0
        ends_with_newline = True
        has_content = False
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                has_content = True
                char_count += len(chunk)
                line_count += chunk.count("\n")
                ends_with_newline = chunk.endswith("\n")
        if has_content and not ends_with_newline:
            line_count += 1
        return line_count, char_count

    def _count_pdf_pages(self, file_path: Path, chunk_size: int = 65536) -> int:
        pattern = b"/Type /Page"
        pattern_len = len(pattern)
        overlap = pattern_len - 1
        count = 0
        with open(file_path, "rb") as f:
            buffer = b""
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                data = buffer + chunk
                count += data.count(pattern)
                if len(data) >= pattern_len:
                    buffer = data[-overlap:]
                else:
                    buffer = data
        return count

    def _create_processing_alert(self, file_item: StoredFile) -> None:
        if file_item.processing_status == "failed":
            alert = Alert(
                file_id=file_item.id,
                level="critical",
                message="File processing failed",
            )
        elif file_item.requires_attention:
            alert = Alert(
                file_id=file_item.id,
                level="warning",
                message=f"File requires attention: {file_item.scan_details}",
            )
        else:
            alert = Alert(
                file_id=file_item.id,
                level="info",
                message="File processed successfully",
            )
        self.session.add(alert)
        self.session.commit()
