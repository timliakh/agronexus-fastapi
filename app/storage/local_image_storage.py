from pathlib import Path

from app.config import config
from app.exceptions import ImageValidationError


class LocalImageStorage:
    def __init__(self) -> None:
        self._upload_dir = config.paths.products_upload_dir
        self._base_dir = config.paths.base_dir
        self._allowed = config.image.allowed_extensions
        self._max_size = config.image.max_file_size

    def ensure_dir(self) -> None:
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, product_id: int, filename: str, content: bytes) -> str:
        if not filename:
            raise ImageValidationError("Filename is required")

        extension = Path(filename).suffix.lower()
        if extension not in self._allowed:
            raise ImageValidationError("Allowed formats: JPG, PNG, WEBP, GIF")

        if len(content) > self._max_size:
            raise ImageValidationError("File size must be under 5 MB")

        self.ensure_dir()
        stored_name = f"{product_id}{extension}"
        (self._upload_dir / stored_name).write_bytes(content)
        return f"/uploads/products/{stored_name}"

    def remove_by_url(self, image_url: str | None) -> None:
        if not image_url or not image_url.startswith("/uploads/products/"):
            return
        file_path = self._base_dir / image_url.lstrip("/")
        if file_path.is_file():
            file_path.unlink()
