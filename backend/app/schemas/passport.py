from datetime import date

from pydantic import BaseModel, Field


class PassportExtraction(BaseModel):
    full_name: str | None = None
    passport_number: str | None = None
    nationality: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    date_of_issue: date | None = None
    date_of_expiry: date | None = None
    place_of_birth: str | None = None
    place_of_issue: str | None = None
    key_values: dict[str, str] = Field(default_factory=dict)

