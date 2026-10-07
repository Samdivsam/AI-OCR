from app.core.exceptions import ProcessingError
from app.schemas.ocr import OCRResult
from app.services.ocr.base import OCRProvider


class ResilientOCRProvider(OCRProvider):
    def __init__(
        self,
        primary: OCRProvider,
        fallback: OCRProvider,
        fallback_error_codes: set[str] | None = None,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._fallback_error_codes = fallback_error_codes or {
            "OCR_CONFIGURATION_ERROR",
            "OCR_PROVIDER_ERROR",
            "OCR_TIMEOUT",
            "INVALID_OCR_RESPONSE",
        }

    async def extract(self, file_bytes: bytes, filename: str, content_type: str) -> OCRResult:
        try:
            return await self._primary.extract(file_bytes, filename, content_type)
        except ProcessingError as exc:
            if exc.code not in self._fallback_error_codes:
                raise
            return await self._fallback.extract(file_bytes, filename, content_type)

