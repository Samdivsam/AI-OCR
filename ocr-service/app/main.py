from __future__ import annotations

import os
from io import BytesIO
from statistics import mean
from typing import Any

import fitz
import numpy as np
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from PIL import Image
from paddleocr import PaddleOCR
from pydantic import BaseModel, Field

app = FastAPI(title="Private OCR Service", version="1.0.0")

OCR_API_KEY = os.getenv("OCR_API_KEY", "internal-ocr-secret")
OCR_LANG = os.getenv("OCR_LANG", "en")
ocr_engine = PaddleOCR(use_angle_cls=True, lang=OCR_LANG, show_log=False)


class OCRPageResponse(BaseModel):
    page_number: int
    text: str
    confidence: float | None = None
    key_values: dict[str, str] = Field(default_factory=dict)
    tables: list[dict[str, Any]] = Field(default_factory=list)
    bounding_boxes: list[dict[str, float]] = Field(default_factory=list)


class OCRResponse(BaseModel):
    text: str
    confidence: float | None = None
    pages: list[OCRPageResponse] = Field(default_factory=list)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=OCRResponse)
async def extract_document(
    file: UploadFile = File(...),
    authorization: str | None = Header(default=None),
) -> OCRResponse:
    validate_auth(authorization)
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    content_type = file.content_type or "application/octet-stream"
    pages = extract_pages(file_bytes, content_type)
    full_text = "\n\n".join(page.text for page in pages if page.text.strip())
    confidence_values = [page.confidence for page in pages if page.confidence is not None]
    return OCRResponse(
        text=full_text,
        confidence=mean(confidence_values) if confidence_values else None,
        pages=pages,
    )


def validate_auth(authorization: str | None) -> None:
    expected = f"Bearer {OCR_API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def extract_pages(file_bytes: bytes, content_type: str) -> list[OCRPageResponse]:
    if content_type == "application/pdf":
        return extract_pdf_pages(file_bytes)
    if content_type in {"image/png", "image/jpeg", "image/jpg"}:
        image = Image.open(BytesIO(file_bytes)).convert("RGB")
        return [run_ocr_on_image(image, 1)]
    raise HTTPException(status_code=400, detail="Unsupported file type")


def extract_pdf_pages(file_bytes: bytes) -> list[OCRPageResponse]:
    document = fitz.open(stream=file_bytes, filetype="pdf")
    pages: list[OCRPageResponse] = []
    for index, page in enumerate(document, start=1):
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.open(BytesIO(pixmap.tobytes("png"))).convert("RGB")
        pages.append(run_ocr_on_image(image, index))
    return pages


def run_ocr_on_image(image: Image.Image, page_number: int) -> OCRPageResponse:
    image_array = np.array(image)
    raw_result = ocr_engine.ocr(image_array, cls=True)
    lines = raw_result[0] if raw_result and raw_result[0] else []

    extracted_lines: list[str] = []
    confidences: list[float] = []
    boxes: list[dict[str, float]] = []

    for item in lines:
        if len(item) < 2:
            continue
        polygon, text_info = item[0], item[1]
        text = (text_info[0] or "").strip()
        confidence = float(text_info[1]) if len(text_info) > 1 and text_info[1] is not None else None
        if text:
            extracted_lines.append(text)
        if confidence is not None:
            confidences.append(confidence)
        boxes.append(to_box(polygon))

    return OCRPageResponse(
        page_number=page_number,
        text="\n".join(extracted_lines),
        confidence=mean(confidences) if confidences else None,
        bounding_boxes=boxes,
    )


def to_box(polygon: list[list[float]]) -> dict[str, float]:
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    return {
        "x": float(min(xs)),
        "y": float(min(ys)),
        "width": float(max(xs) - min(xs)),
        "height": float(max(ys) - min(ys)),
    }

