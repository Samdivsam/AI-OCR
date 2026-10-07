from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import DocumentStatus, DocumentType, ORMModel


class DocumentResponse(ORMModel):
    id: UUID
    document_type: DocumentType
    original_filename: str
    mime_type: str
    file_size: int
    status: DocumentStatus
    created_at: datetime
    processed_at: datetime | None = None


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class ExtractionResponse(BaseModel):
    document_id: UUID
    document_type: DocumentType
    status: DocumentStatus
    extraction: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = None
    extraction_version: str | None = None


class DashboardSummary(BaseModel):
    total_documents: int
    by_type: dict[str, int]
    recent_documents: list[DocumentResponse]


class UploadResponse(ExtractionResponse):
    pass

