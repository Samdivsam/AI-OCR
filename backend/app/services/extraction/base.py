from abc import ABC, abstractmethod
from typing import Any

from app.schemas.ocr import OCRResult


class DocumentExtractor(ABC):
    @abstractmethod
    def extract(self, ocr_result: OCRResult) -> dict[str, Any]:
        raise NotImplementedError

