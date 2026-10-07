from decimal import Decimal
from typing import Any


class DataNormalizationService:
    def normalize(self, extraction: dict[str, Any]) -> dict[str, Any]:
        return self._walk(extraction)

    def _walk(self, value: Any) -> Any:
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, dict):
            return {key: self._walk(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._walk(item) for item in value]
        return value

