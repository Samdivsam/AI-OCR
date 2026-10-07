import httpx

from app.core.config import Settings
from app.core.exceptions import ProcessingError
from app.schemas.ocr import OCRPage, OCRResult
from app.services.ocr.base import OCRProvider


class ExternalOCRProvider(OCRProvider):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def extract(self, file_bytes: bytes, filename: str, content_type: str) -> OCRResult:
        if not self._settings.ocr_api_url or not self._settings.ocr_api_key:
            raise ProcessingError("OCR_CONFIGURATION_ERROR", "External OCR provider is not configured.")

        headers = {"Authorization": f"Bearer {self._settings.ocr_api_key}"}
        timeout = httpx.Timeout(float(self._settings.http_timeout_seconds))
        files = {"file": (filename, file_bytes, content_type)}

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self._settings.ocr_api_url, files=files, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise ProcessingError("OCR_TIMEOUT", "OCR provider timed out.") from exc
        except httpx.HTTPError as exc:
            raise ProcessingError("OCR_PROVIDER_ERROR", "OCR provider request failed.") from exc
        except ValueError as exc:
            raise ProcessingError("INVALID_OCR_RESPONSE", "OCR provider returned invalid JSON.") from exc

        text = payload.get("text") or "\n".join(page.get("text", "") for page in payload.get("pages", []))
        if not text:
            raise ProcessingError("INVALID_OCR_RESPONSE", "OCR response did not contain readable text.")

        pages = [
            OCRPage(
                page_number=page.get("page_number", index + 1),
                text=page.get("text", ""),
                confidence=page.get("confidence"),
                key_values=page.get("key_values", {}),
                tables=page.get("tables", []),
                bounding_boxes=page.get("bounding_boxes", []),
            )
            for index, page in enumerate(payload.get("pages", []))
        ]
        return OCRResult(text=text, confidence=payload.get("confidence"), pages=pages, raw_response=payload)

