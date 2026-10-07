from __future__ import annotations

from io import BytesIO
from statistics import mean

import fitz
import pytesseract
from PIL import Image, ImageOps
from pypdf import PdfReader
from pytesseract import Output

from app.core.exceptions import ProcessingError
from app.schemas.ocr import OCRPage, OCRResult
from app.services.ocr.base import OCRProvider


class LocalOCRProvider(OCRProvider):
    """Local OCR provider that keeps document parsing inside the application."""

    async def extract(self, file_bytes: bytes, filename: str, content_type: str) -> OCRResult:
        try:
            if content_type == "application/pdf":
                return self._extract_from_pdf(file_bytes)
            if content_type in {"image/png", "image/jpeg", "image/jpg"}:
                return self._extract_from_image(file_bytes)
        except ProcessingError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise ProcessingError("LOCAL_OCR_FAILED", "Unable to process the uploaded document locally.") from exc

        raise ProcessingError("UNSUPPORTED_FILE_TYPE", "Local OCR does not support this file type.")

    def _extract_from_pdf(self, file_bytes: bytes) -> OCRResult:
        text_pages = self._extract_pdf_text(file_bytes)
        if any(page.text.strip() for page in text_pages):
            full_text = "\n\n".join(page.text for page in text_pages if page.text.strip())
            confidence_values = [page.confidence for page in text_pages if page.confidence is not None]
            return OCRResult(
                text=full_text,
                confidence=mean(confidence_values) if confidence_values else 1.0,
                pages=text_pages,
                raw_response={"provider": "local", "source": "pdf-text"},
            )

        ocr_pages = self._ocr_rendered_pdf(file_bytes)
        full_text = "\n\n".join(page.text for page in ocr_pages if page.text.strip())
        confidence_values = [page.confidence for page in ocr_pages if page.confidence is not None]
        return OCRResult(
            text=full_text,
            confidence=mean(confidence_values) if confidence_values else None,
            pages=ocr_pages,
            raw_response={"provider": "local", "source": "pdf-render-ocr"},
        )

    def _extract_pdf_text(self, file_bytes: bytes) -> list[OCRPage]:
        pages: list[OCRPage] = []
        reader = PdfReader(BytesIO(file_bytes))
        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            pages.append(OCRPage(page_number=index, text=text, confidence=1.0 if text else None))
        return pages

    def _ocr_rendered_pdf(self, file_bytes: bytes) -> list[OCRPage]:
        try:
            document = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:  # noqa: BLE001
            raise ProcessingError("PDF_READ_FAILED", "Unable to read the uploaded PDF.") from exc

        pages: list[OCRPage] = []
        for index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image_bytes = pixmap.tobytes("png")
            pages.append(self._ocr_page(Image.open(BytesIO(image_bytes)), index))
        return pages

    def _extract_from_image(self, file_bytes: bytes) -> OCRResult:
        try:
            image = Image.open(BytesIO(file_bytes))
        except Exception as exc:  # noqa: BLE001
            raise ProcessingError("IMAGE_READ_FAILED", "Unable to read the uploaded image.") from exc

        page = self._ocr_page(image, 1)
        return OCRResult(
            text=page.text,
            confidence=page.confidence,
            pages=[page],
            raw_response={"provider": "local", "source": "image-ocr"},
        )

    def _ocr_page(self, image: Image.Image, page_number: int) -> OCRPage:
        try:
            normalized_image = ImageOps.grayscale(image).convert("L")
            data = pytesseract.image_to_data(normalized_image, output_type=Output.DICT)
            text = pytesseract.image_to_string(normalized_image).strip()
        except pytesseract.TesseractNotFoundError as exc:
            raise ProcessingError(
                "LOCAL_OCR_DEPENDENCY_MISSING",
                "Tesseract OCR is not installed in the runtime environment.",
            ) from exc

        confidences = [float(value) for value in data.get("conf", []) if value not in {"-1", -1, ""}]
        confidence = mean(confidences) / 100 if confidences else None
        return OCRPage(page_number=page_number, text=text, confidence=confidence)

