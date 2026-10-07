import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.schemas.common import DocumentStatus, DocumentType


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_user_id", "user_id"),
        Index("ix_documents_document_type", "document_type"),
        Index("ix_documents_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), default=DocumentType.OTHER.value, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=DocumentStatus.PROCESSING.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="documents")
    extraction = relationship(
        "DocumentExtraction",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
    )


