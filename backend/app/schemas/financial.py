from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class FinancialSummaryResponse(BaseModel):
    total_income: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    net_cash_flow: Decimal = Decimal("0")
    transaction_count: int = 0


class FinancialTransactionResponse(BaseModel):
    document_id: str
    transaction_date: date | None = None
    description: str | None = None
    reference_number: str | None = None
    debit: Decimal | None = None
    credit: Decimal | None = None
    balance: Decimal | None = None
    transaction_type: str | None = None


class MonthlySummaryItem(BaseModel):
    month: str
    income: Decimal = Decimal("0")
    expenses: Decimal = Decimal("0")
    net: Decimal = Decimal("0")


class MonthlySummaryResponse(BaseModel):
    items: list[MonthlySummaryItem] = Field(default_factory=list)

