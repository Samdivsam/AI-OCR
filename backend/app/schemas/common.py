from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentType(StrEnum):
    ID_CARD = "ID_CARD"
    PASSPORT = "PASSPORT"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    BANK_STATEMENT = "BANK_STATEMENT"
    SALARY_SLIP = "SALARY_SLIP"
    OTHER = "OTHER"


class DocumentStatus(StrEnum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class APIErrorDetail(BaseModel):
    code: str
    message: str


class APIErrorResponse(BaseModel):
    error: APIErrorDetail


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class TokenPayload(BaseModel):
    sub: UUID

