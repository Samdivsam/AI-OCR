from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import BadRequestError

ALLOWED_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    "application/pdf": (b"%PDF",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/jpeg": (b"\xff\xd8\xff",),
}

ALLOWED_EXTENSIONS = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


class FileValidationResult:
    def __init__(self, mime_type: str, extension: str, size: int) -> None:
        self.mime_type = mime_type
        self.extension = extension
        self.size = size



def validate_upload(file_bytes: bytes, filename: str, content_type: str | None, settings: Settings) -> FileValidationResult:
    if not file_bytes:
        raise BadRequestError("EMPTY_FILE", "Uploaded file is empty.")

    size = len(file_bytes)
    if size > settings.max_upload_size_bytes:
        raise BadRequestError("FILE_TOO_LARGE", f"File exceeds the maximum size of {settings.max_upload_size_mb} MB.")

    extension = Path(filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise BadRequestError("UNSUPPORTED_FILE_TYPE", "Only PDF, JPG, JPEG, and PNG files are supported.")

    detected_mime = ALLOWED_EXTENSIONS[extension]
    signatures = ALLOWED_SIGNATURES[detected_mime]
    if not any(file_bytes.startswith(signature) for signature in signatures):
        raise BadRequestError("INVALID_FILE_SIGNATURE", "Uploaded file signature does not match the supported file type.")

    if content_type and detected_mime != content_type and not (
        detected_mime == "image/jpeg" and content_type == "image/jpg"
    ):
        raise BadRequestError("MIME_TYPE_MISMATCH", "Uploaded file MIME type does not match its content.")

    return FileValidationResult(mime_type=detected_mime, extension=extension, size=size)

