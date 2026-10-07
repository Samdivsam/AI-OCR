from app.core.exceptions import ProcessingError
from app.core.config import Settings
from app.services.ocr.base import OCRProvider
from app.services.ocr.external import ExternalOCRProvider
from app.services.ocr.local import LocalOCRProvider
from app.services.ocr.mock import MockOCRProvider
from app.services.ocr.resilient import ResilientOCRProvider


class OCRProviderFactory:
    @staticmethod
    def create(settings: Settings) -> OCRProvider:
        if settings.ocr_provider == "external":
            return ResilientOCRProvider(ExternalOCRProvider(settings), LocalOCRProvider())
        if settings.ocr_provider == "local":
            return LocalOCRProvider()
        if settings.ocr_provider == "mock":
            return MockOCRProvider()
        raise ProcessingError("OCR_CONFIGURATION_ERROR", f"Unsupported OCR provider: {settings.ocr_provider}")

