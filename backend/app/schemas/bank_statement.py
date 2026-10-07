from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BankTransaction(BaseModel):
    transaction_date: date | None = None
    description: str | None = None
    reference_number: str | None = None
    debit: Decimal | None = None
    credit: Decimal | None = None
    balance: Decimal | None = None
    transaction_type: str | None = None


class BankStatementExtraction(BaseModel):
    bank_name: str | None = None
    account_holder: str | None = None
    account_number: str | None = None
    account_type: str | None = None
    statement_start: date | None = None
    statement_end: date | None = None
    opening_balance: Decimal | None = None
    closing_balance: Decimal | None = None
    transactions: list[BankTransaction] = Field(default_factory=list)
    key_values: dict[str, str] = Field(default_factory=dict)

