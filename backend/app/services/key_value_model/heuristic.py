import re
from typing import Any

from app.schemas.common import DocumentType
from app.services.extraction.helpers import extract_key_value_pairs, normalize_ocr_text
from app.services.key_value_model.base import KeyValueModel


class HeuristicKeyValueModel(KeyValueModel):
    metadata_keys = {"key_values", "ocr_text_preview", "raw_text_preview", "extraction_warning", "structured_fields_detected"}
    label_line_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9/&()'.,\-\s]{1,50}$")
    numeric_or_date_pattern = re.compile(r"^(?:\d[\d,./\- ]*|[A-Z0-9\-]{4,})$")

    def transform(self, document_type: DocumentType, raw_text: str, extracted_data: dict[str, Any]) -> dict[str, Any]:
        merged = dict(extracted_data)
        key_values = self._build_key_values(document_type, raw_text, extracted_data)
        merged["key_values"] = key_values
        return merged

    def _build_key_values(self, document_type: DocumentType, raw_text: str, extracted_data: dict[str, Any]) -> dict[str, str]:
        normalized_text = normalize_ocr_text(raw_text)
        lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]
        pairs: dict[str, str] = {}

        heading_pair = self._extract_heading_pair(document_type, lines)
        if heading_pair is not None:
            key, value = heading_pair
            pairs[key] = value

        for key, value in extract_key_value_pairs(normalized_text).items():
            pairs.setdefault(key, value)

        for key, value in self._extract_multiline_pairs(lines).items():
            pairs.setdefault(key, value)

        for key, value in self._pairs_from_structured_data(extracted_data).items():
            pairs.setdefault(key, value)

        return pairs

    def _extract_heading_pair(self, document_type: DocumentType, lines: list[str]) -> tuple[str, str] | None:
        if document_type != DocumentType.BANK_STATEMENT or len(lines) < 2:
            return None
        first, second = lines[0], lines[1]
        if ":" in first or ":" in second:
            return None
        if len(first) > 60 or len(second) > 80:
            return None
        upper_first = first.upper()
        upper_second = second.upper()
        if "BANK" in upper_first and any(token in upper_second for token in ["STATEMENT", "ACCOUNT", "SUMMARY"]):
            return first.title() if first.isupper() else first, second.title() if second.isupper() else second
        return None

    def _extract_multiline_pairs(self, lines: list[str]) -> dict[str, str]:
        pairs: dict[str, str] = {}
        index = 0
        while index < len(lines) - 1:
            key = lines[index]
            value = lines[index + 1]
            if self._looks_like_label(key) and self._looks_like_value(value):
                cleaned_key = self._clean_key(key)
                cleaned_value = self._clean_value(value)
                if cleaned_key and cleaned_value:
                    pairs.setdefault(cleaned_key, cleaned_value)
                    index += 2
                    continue
            index += 1
        return pairs

    def _pairs_from_structured_data(self, extracted_data: dict[str, Any]) -> dict[str, str]:
        pairs: dict[str, str] = {}
        for key, value in extracted_data.items():
            if key in self.metadata_keys or value in (None, "", [], {}):
                continue
            if isinstance(value, dict):
                continue
            if isinstance(value, list):
                if value and all(not isinstance(item, (dict, list)) for item in value):
                    pairs[self._humanize_key(key)] = ", ".join(str(item) for item in value if item not in (None, ""))
                continue
            pairs[self._humanize_key(key)] = str(value)
        return pairs

    def _looks_like_label(self, line: str) -> bool:
        if ":" in line:
            return False
        if not self.label_line_pattern.fullmatch(line):
            return False
        upper = line.upper()
        blocked_tokens = ["DATE", "DESCRIPTION", "BALANCE", "DEPOSITS", "WITHDRAWALS", "TOTALS", "PAGE"]
        return not (len(line) < 3 or any(token == upper for token in blocked_tokens))

    def _looks_like_value(self, line: str) -> bool:
        if not line or len(line) > 120:
            return False
        if ":" in line:
            return False
        return bool(self.numeric_or_date_pattern.fullmatch(line) or not self._looks_like_label(line))

    def _clean_key(self, key: str) -> str:
        cleaned = re.sub(r"\s+", " ", key).strip(" :-#\t.")
        if cleaned.isupper() and len(cleaned) <= 4:
            return cleaned
        return cleaned.title() if cleaned.isupper() else cleaned

    def _clean_value(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip(" :-#\t,")

    def _humanize_key(self, key: str) -> str:
        return key.replace("_", " ").strip().title()


