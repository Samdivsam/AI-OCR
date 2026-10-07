from abc import ABC, abstractmethod
from typing import Any

from app.schemas.common import DocumentType


class KeyValueModel(ABC):
    @abstractmethod
    def transform(self, document_type: DocumentType, raw_text: str, extracted_data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

