from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.core.exceptions import NotFoundError, ProcessingError
from app.db.models.document import Document
from app.db.models.extraction import DocumentExtraction
from app.db.models.user import User
from app.schemas.common import DocumentStatus, DocumentType
from app.schemas.document import DashboardSummary, DocumentListResponse, DocumentResponse, ExtractionResponse
from app.services.classification.classifier import DocumentClassifier
from app.services.extraction.registry import ExtractorRegistry
from app.services.ocr.base import OCRProvider
from app.services.validation.normalization import DataNormalizationService
from app.utils.file_validation import validate_upload


class DocumentService:
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        ocr_provider: OCRProvider,
        classifier: DocumentClassifier,
        extractor_registry: ExtractorRegistry,
        normalizer: DataNormalizationService,
    ) -> None:
        self.session = session
        self.settings = settings
        self.ocr_provider = ocr_provider
        self.classifier = classifier
        self.extractor_registry = extractor_registry
        self.normalizer = normalizer

    async def process_upload(
        self,
        user: User,
        filename: str,
        content_type: str | None,
        file_bytes: bytes,
        requested_document_type: DocumentType | None = None,
    ) -> ExtractionResponse:
        metadata = validate_upload(file_bytes, filename, content_type, self.settings)
        document = Document(
            user_id=user.id,
            original_filename=filename or "uploaded-document",
            mime_type=metadata.mime_type,
            file_size=metadata.size,
            status=DocumentStatus.PROCESSING.value,
            document_type=DocumentType.OTHER.value,
        )
        self.session.add(document)
        await self.session.flush()

        try:
            ocr_result = await self.ocr_provider.extract(file_bytes, document.original_filename, metadata.mime_type)
            if not ocr_result.text.strip():
                raise ProcessingError("INVALID_OCR_RESPONSE", "Unable to extract readable text from the document.")
            document_type = requested_document_type or self.classifier.classify(ocr_result)
            extractor = self.extractor_registry.get(document_type)
            extracted_data = self.normalizer.normalize(extractor.extract(ocr_result))
            extracted_data = self._enrich_extraction_result(extracted_data, ocr_result.text)

            document.document_type = document_type.value
            document.status = DocumentStatus.COMPLETED.value
            document.processed_at = datetime.now(UTC)
            extraction = DocumentExtraction(
                document_id=document.id,
                raw_ocr_text=ocr_result.text if self.settings.store_raw_ocr_text else None,
                extracted_data=extracted_data,
                confidence=ocr_result.confidence,
                extraction_version=self.settings.extraction_version,
            )
            self.session.add(extraction)
            await self.session.commit()
            return ExtractionResponse(
                document_id=document.id,
                document_type=document_type,
                status=DocumentStatus.COMPLETED,
                extraction=extracted_data,
                confidence=ocr_result.confidence,
                extraction_version=extraction.extraction_version,
            )
        except Exception:
            document.status = DocumentStatus.FAILED.value
            document.processed_at = datetime.now(UTC)
            await self.session.commit()
            raise

    def _enrich_extraction_result(self, extracted_data: dict[str, Any], raw_text: str) -> dict[str, Any]:
        preview = raw_text.strip()[:1500]
        enriched = dict(extracted_data)
        enriched.setdefault("ocr_text_preview", preview)

        structured_count = sum(
            1
            for key, value in extracted_data.items()
            if key != "raw_text_preview" and self._has_meaningful_value(value)
        )
        enriched["structured_fields_detected"] = structured_count

        if structured_count == 0 and preview:
            enriched.setdefault(
                "extraction_warning",
                "Structured field extraction was limited. Review the OCR text preview below.",
            )

        return enriched

    def _has_meaningful_value(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, dict):
            return any(self._has_meaningful_value(item) for item in value.values())
        if isinstance(value, list):
            return any(self._has_meaningful_value(item) for item in value)
        return True

    async def list_documents(self, user: User) -> DocumentListResponse:
        result = await self.session.execute(
            select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())
        )
        items = list(result.scalars().all())
        return DocumentListResponse(items=[DocumentResponse.model_validate(item) for item in items], total=len(items))

    async def get_document(self, user: User, document_id: UUID) -> Document:
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.extraction))
            .where(Document.id == document_id, Document.user_id == user.id)
        )
        document = result.scalar_one_or_none()
        if document is None:
            raise NotFoundError("Document not found.")
        return document

    async def get_extraction(self, user: User, document_id: UUID) -> ExtractionResponse:
        document = await self.get_document(user, document_id)
        extraction = document.extraction
        if extraction is None:
            raise NotFoundError("Extraction not found.")
        return ExtractionResponse(
            document_id=document.id,
            document_type=DocumentType(document.document_type),
            status=DocumentStatus(document.status),
            extraction=extraction.extracted_data,
            confidence=extraction.confidence,
            extraction_version=extraction.extraction_version,
        )

    async def delete_document(self, user: User, document_id: UUID) -> None:
        document = await self.get_document(user, document_id)
        await self.session.delete(document)
        await self.session.commit()

    async def dashboard(self, user: User) -> DashboardSummary:
        count_result = await self.session.execute(
            select(func.count(Document.id)).where(Document.user_id == user.id)
        )
        total_documents = count_result.scalar_one()

        by_type_result = await self.session.execute(
            select(Document.document_type, func.count(Document.id))
            .where(Document.user_id == user.id)
            .group_by(Document.document_type)
        )
        by_type = {doc_type: total for doc_type, total in by_type_result.all()}

        recent_result = await self.session.execute(
            select(Document)
            .where(Document.user_id == user.id)
            .order_by(Document.created_at.desc())
            .limit(5)
        )
        recent_documents = [DocumentResponse.model_validate(item) for item in recent_result.scalars().all()]
        return DashboardSummary(
            total_documents=total_documents,
            by_type=by_type,
            recent_documents=recent_documents,
        )

    async def bank_statement_extractions(self, user: User) -> list[tuple[UUID, dict[str, Any]]]:
        result = await self.session.execute(
            select(Document.id, DocumentExtraction.extracted_data)
            .join(DocumentExtraction, DocumentExtraction.document_id == Document.id)
            .where(Document.user_id == user.id, Document.document_type == DocumentType.BANK_STATEMENT.value)
        )
        return [(document_id, extracted_data) for document_id, extracted_data in result.all()]

