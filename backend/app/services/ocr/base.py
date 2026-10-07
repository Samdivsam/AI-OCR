from abc import ABC, abstractmethod

from app.schemas.ocr import OCRResult


class OCRProvider(ABC):
    @abstractmethod
    async def extract(self, file_bytes: bytes, filename: str, content_type: str) -> OCRResult:
        raise NotImplementedError

