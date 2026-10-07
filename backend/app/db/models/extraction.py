import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base

json_type = JSON().with_variant(JSONB, "postgresql")


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    __table_args__ = (Index("ix_document_extractions_document_id", "document_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    raw_ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_data: Mapped[dict] = mapped_column(json_type, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extraction_version: Mapped[str] = mapped_column(String(20), default="v1", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    document = relationship("Document", back_populates="extraction")


