from datetime import date

from pydantic import BaseModel, Field


class IDCardExtraction(BaseModel):
    name: str | None = None
    father_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    document_number: str | None = None
    address: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    key_values: dict[str, str] = Field(default_factory=dict)

