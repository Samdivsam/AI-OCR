from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import DBSession, get_current_user
from app.core.config import Settings, get_settings
from app.db.models.user import User
from app.schemas.financial import FinancialSummaryResponse, FinancialTransactionResponse, MonthlySummaryResponse
from app.services.classification.classifier import DocumentClassifier
from app.services.documents.service import DocumentService
from app.services.extraction.registry import ExtractorRegistry
from app.services.financial.service import FinancialAnalysisService
from app.services.key_value_model.factory import KeyValueModelFactory
from app.services.ocr.factory import OCRProviderFactory
from app.services.validation.normalization import DataNormalizationService

router = APIRouter(prefix="/financial", tags=["financial"])


def build_document_service(session: DBSession, settings: Settings) -> DocumentService:
    return DocumentService(
        session=session,
        settings=settings,
        ocr_provider=OCRProviderFactory.create(settings),
        classifier=DocumentClassifier(),
        extractor_registry=ExtractorRegistry(),
        key_value_model=KeyValueModelFactory.create(settings),
        normalizer=DataNormalizationService(),
    )


@router.get("/summary", response_model=FinancialSummaryResponse)
async def get_summary(
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FinancialSummaryResponse:
    documents = await build_document_service(session, settings).bank_statement_extractions(current_user)
    return FinancialAnalysisService().summarize(documents)


@router.get("/transactions", response_model=list[FinancialTransactionResponse])
async def get_transactions(
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[FinancialTransactionResponse]:
    documents = await build_document_service(session, settings).bank_statement_extractions(current_user)
    return FinancialAnalysisService().list_transactions(documents)


@router.get("/monthly-summary", response_model=MonthlySummaryResponse)
async def get_monthly_summary(
    session: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> MonthlySummaryResponse:
    documents = await build_document_service(session, settings).bank_statement_extractions(current_user)
    return FinancialAnalysisService().monthly_summary(documents)

