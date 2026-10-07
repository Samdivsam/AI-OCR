from datetime import date

from pydantic import BaseModel, Field


class DrivingLicenseExtraction(BaseModel):
    name: str | None = None
    father_name: str | None = None
    date_of_birth: date | None = None
    license_number: str | None = None
    address: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    vehicle_classes: list[str] = Field(default_factory=list)
    key_values: dict[str, str] = Field(default_factory=dict)

