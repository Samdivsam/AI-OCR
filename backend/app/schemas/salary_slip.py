from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class SalarySlipExtraction(BaseModel):
    employee_name: str | None = None
    employee_id: str | None = None
    employer_name: str | None = None
    pay_period: date | None = None
    basic_salary: Decimal | None = None
    allowances: Decimal | None = None
    deductions: Decimal | None = None
    gross_salary: Decimal | None = None
    net_salary: Decimal | None = None
    tax: Decimal | None = None
    other_deductions: Decimal | None = None
    key_values: dict[str, str] = Field(default_factory=dict)

