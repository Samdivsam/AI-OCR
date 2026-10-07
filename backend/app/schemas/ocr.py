from typing import Any

from pydantic import BaseModel, Field


class OCRBoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class OCRPage(BaseModel):
    page_number: int
    text: str
    confidence: float | None = None
    key_values: dict[str, str] = Field(default_factory=dict)
    tables: list[dict[str, Any]] = Field(default_factory=list)
    bounding_boxes: list[OCRBoundingBox] = Field(default_factory=list)


class OCRResult(BaseModel):
    text: str
    confidence: float | None = None
    pages: list[OCRPage] = Field(default_factory=list)
    raw_response: dict[str, Any] | None = None

