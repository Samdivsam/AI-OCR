from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import DBSession, get_current_user
from app.core.config import Settings, get_settings
from app.db.models.user import User
from app.schemas.common import DocumentType, MessageResponse
from app.schemas.document import DashboardSummary, DocumentListResponse, DocumentResponse, ExtractionResponse, UploadResponse
from app.services.classification.classifier import DocumentClassifier
from app.services.documents.service import DocumentService
from app.services.extraction.registry import ExtractorRegistry
from app.services.ocr.factory import OCRProviderFactory
from app.services.validation.normalization import DataNormalizationService

router = APIRouter(prefix="/documents", tags=["documents"])


def build_document_service(session: DBSession, settings: Settings) -> DocumentService:
    return DocumentService(
        session=session,
        settings=settings,
        ocr_provider=OCRProviderFactory.create(settings),
        classifier=DocumentClassifier(),
        extractor_registry=ExtractorRegistry(),
        normalizer=DataNormalizationService(),
    )


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
    document_type: Annotated[DocumentType | None, Form()] = None,
    file: UploadFile = File(...),
) -> UploadResponse:
    file_bytes = await file.read()
    service = build_document_service(session, settings)
    result = await service.process_upload(
        current_user,
        file.filename or "uploaded-document",
        file.content_type,
        file_bytes,
        document_type,
    )
    return UploadResponse.model_validate(result.model_dump())


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentListResponse:
    return await build_document_service(session, settings).list_documents(current_user)


@router.get("/dashboard", response_model=DashboardSummary)
async def dashboard(
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DashboardSummary:
    return await build_document_service(session, settings).dashboard(current_user)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentResponse:
    document = await build_document_service(session, settings).get_document(current_user, document_id)
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/extraction", response_model=ExtractionResponse)
async def get_extraction(
    document_id: UUID,
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExtractionResponse:
    return await build_document_service(session, settings).get_extraction(current_user, document_id)


@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: UUID,
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> MessageResponse:
    await build_document_service(session, settings).delete_document(current_user, document_id)
    return MessageResponse(message="Document deleted successfully.")


