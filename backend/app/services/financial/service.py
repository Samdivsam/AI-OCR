from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.schemas.financial import (
    FinancialSummaryResponse,
    FinancialTransactionResponse,
    MonthlySummaryItem,
    MonthlySummaryResponse,
)


class FinancialAnalysisService:
    def _iter_transactions(self, documents: list[tuple[UUID, dict[str, Any]]]):
        for document_id, extraction in documents:
            for item in extraction.get("transactions", []):
                yield FinancialTransactionResponse(document_id=str(document_id), **item)

    def summarize(self, documents: list[tuple[UUID, dict[str, Any]]]) -> FinancialSummaryResponse:
        income = Decimal("0")
        expenses = Decimal("0")
        count = 0
        for tx in self._iter_transactions(documents):
            count += 1
            if tx.credit:
                income += tx.credit
            if tx.debit:
                expenses += tx.debit
        return FinancialSummaryResponse(
            total_income=income,
            total_expenses=expenses,
            net_cash_flow=income - expenses,
            transaction_count=count,
        )

    def list_transactions(self, documents: list[tuple[UUID, dict[str, Any]]]) -> list[FinancialTransactionResponse]:
        return sorted(
            self._iter_transactions(documents),
            key=lambda item: item.transaction_date or date.min,
            reverse=True,
        )

    def monthly_summary(self, documents: list[tuple[UUID, dict[str, Any]]]) -> MonthlySummaryResponse:
        buckets: dict[str, dict[str, Decimal]] = defaultdict(
            lambda: {"income": Decimal("0"), "expenses": Decimal("0")}
        )
        for tx in self._iter_transactions(documents):
            month = (tx.transaction_date or date.today()).strftime("%Y-%m")
            if tx.credit:
                buckets[month]["income"] += tx.credit
            if tx.debit:
                buckets[month]["expenses"] += tx.debit

        items = [
            MonthlySummaryItem(
                month=month,
                income=values["income"],
                expenses=values["expenses"],
                net=values["income"] - values["expenses"],
            )
            for month, values in sorted(buckets.items())
        ]
        return MonthlySummaryResponse(items=items)

