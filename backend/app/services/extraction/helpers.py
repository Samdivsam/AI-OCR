import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d %b %Y", "%d %B %Y"]
DATE_REGEX = re.compile(r"\b(?:\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b")


def normalize_ocr_text(text: str) -> str:
    return (
        text.replace("\r", "\n")
        .replace("\t", " ")
        .replace("’", "'")
        .replace("–", "-")
        .replace("—", "-")
    )


def _alias_pattern(aliases: list[str]) -> str:
    return "|".join(f"(?:{alias})" for alias in aliases)


def _clean_value(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" :-#\t")


def extract_regex_value(text: str, patterns: list[str]) -> str | None:
    normalized = normalize_ocr_text(text)
    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE | re.MULTILINE)
        if match:
            candidate = next((group for group in match.groups() if group), match.group(0))
            cleaned = _clean_value(candidate)
            if cleaned:
                return cleaned
    return None


def extract_labeled_value(
    text: str,
    aliases: list[str],
    *,
    multiline: bool = False,
    stop_aliases: list[str] | None = None,
) -> str | None:
    normalized = normalize_ocr_text(text)
    alias_group = _alias_pattern(aliases)
    stop_group = _alias_pattern(stop_aliases or []) if stop_aliases else None
    lines = [line.strip() for line in normalized.splitlines()]

    inline_pattern = re.compile(
        rf"^\s*(?:{alias_group})\b\s*(?:[:=\-]|\s{{1,4}})\s*(?P<value>.+?)\s*$",
        re.IGNORECASE,
    )
    label_only_pattern = re.compile(
        rf"^\s*(?:{alias_group})\b\s*[:=\-]?\s*$",
        re.IGNORECASE,
    )
    stop_pattern = re.compile(rf"^\s*(?:{stop_group})\b", re.IGNORECASE) if stop_group else None

    for index, line in enumerate(lines):
        if not line:
            continue
        inline_match = inline_pattern.match(line)
        if inline_match:
            value = _clean_value(inline_match.group("value"))
            if multiline:
                extra = _collect_following_lines(lines, index + 1, stop_pattern)
                if extra:
                    value = _clean_value(f"{value} {' '.join(extra)}")
            if value:
                return value

        if label_only_pattern.match(line):
            extra = _collect_following_lines(lines, index + 1, stop_pattern)
            if extra:
                return _clean_value(" ".join(extra))
    return None


def _collect_following_lines(lines: list[str], start_index: int, stop_pattern: re.Pattern[str] | None) -> list[str]:
    collected: list[str] = []
    for line in lines[start_index:]:
        candidate = line.strip()
        if not candidate:
            if collected:
                break
            continue
        if stop_pattern and stop_pattern.match(candidate):
            break
        if re.match(r"^[A-Za-z][A-Za-z\s]{2,30}\s*[:=\-]", candidate) and collected:
            break
        collected.append(candidate)
        if len(collected) >= 3:
            break
    return collected


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    cleaned = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    range_match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})", cleaned)
    if range_match:
        return parse_date(range_match.group(1))
    return None


def extract_first_date(text: str) -> date | None:
    normalized = normalize_ocr_text(text)
    for match in DATE_REGEX.findall(normalized):
        parsed = parse_date(match)
        if parsed:
            return parsed
    return None


def extract_all_dates(text: str) -> list[date]:
    normalized = normalize_ocr_text(text)
    results: list[date] = []
    for match in DATE_REGEX.findall(normalized):
        parsed = parse_date(match)
        if parsed and parsed not in results:
            results.append(parsed)
    return results


def parse_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    cleaned = re.sub(r"[^0-9.-]", "", value)
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def normalize_gender(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower()
    mapping = {"m": "Male", "male": "Male", "f": "Female", "female": "Female"}
    return mapping.get(normalized, value.strip().title())


def extract_key_value_pairs(text: str, max_pairs: int = 50) -> dict[str, str]:
    """Extract simple key-value pairs from OCR text in 'Key: Value' format."""
    normalized = normalize_ocr_text(text)
    pairs: dict[str, str] = {}
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]

    for line in lines:
        if ":" not in line or len(line) < 5:
            continue
        parts = line.split(":", maxsplit=1)
        if len(parts) != 2:
            continue
        key = parts[0].strip()
        value = parts[1].strip()
        if not key or not value:
            continue
        if len(key) > 80 or len(value) > 250:
            continue
        if re.match(r"^[a-zA-Z0-9\s\-()./&',]*$", key) and re.match(r"^[a-zA-Z0-9\s\-()./&',%.]*$", value):
            pairs[key] = value
            if len(pairs) >= max_pairs:
                break

    return pairs


