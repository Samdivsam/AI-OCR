from decimal import Decimal

import pytest

from app.core.exceptions import ProcessingError
from app.schemas.common import DocumentType
from app.schemas.ocr import OCRPage
from app.schemas.ocr import OCRResult
from app.services.classification.classifier import DocumentClassifier
from app.services.extraction.extractors import (
    BankStatementExtractor,
    DrivingLicenseExtractor,
    IDCardExtractor,
    PassportExtractor,
    SalarySlipExtractor,
)
from app.services.financial.service import FinancialAnalysisService
from app.services.key_value_model.heuristic import HeuristicKeyValueModel
from app.services.ocr.base import OCRProvider
from app.services.ocr.mock import MockOCRProvider
from app.services.ocr.resilient import ResilientOCRProvider


class StubOCRProvider(OCRProvider):
    def __init__(self, result: OCRResult | None = None, error: Exception | None = None) -> None:
        self._result = result
        self._error = error

    async def extract(self, file_bytes: bytes, filename: str, content_type: str) -> OCRResult:
        if self._error is not None:
            raise self._error
        assert self._result is not None
        return self._result


@pytest.mark.asyncio
async def test_mock_ocr_success(sample_pdf_bytes) -> None:
    result = await MockOCRProvider().extract(sample_pdf_bytes, "id-card.pdf", "application/pdf")
    assert "John Doe" in result.text
    assert result.confidence is not None


@pytest.mark.asyncio
async def test_mock_ocr_failure(sample_pdf_bytes) -> None:
    with pytest.raises(RuntimeError):
        await MockOCRProvider().extract(sample_pdf_bytes, "fail.pdf", "application/pdf")


@pytest.mark.asyncio
async def test_mock_ocr_malformed_response(sample_pdf_bytes) -> None:
    result = await MockOCRProvider().extract(sample_pdf_bytes, "malformed.pdf", "application/pdf")
    assert result.text == ""
    assert result.raw_response == {"unexpected": True}


@pytest.mark.asyncio
async def test_mock_ocr_low_confidence(sample_pdf_bytes) -> None:
    result = await MockOCRProvider().extract(sample_pdf_bytes, "low-confidence-id.pdf", "application/pdf")
    assert result.confidence == 0.45


@pytest.mark.asyncio
async def test_resilient_ocr_provider_falls_back_on_timeout(sample_pdf_bytes) -> None:
    primary = StubOCRProvider(error=ProcessingError("OCR_TIMEOUT", "OCR provider timed out."))
    fallback_result = OCRResult(
        text="Recovered locally",
        confidence=0.91,
        pages=[OCRPage(page_number=1, text="Recovered locally", confidence=0.91)],
    )
    provider = ResilientOCRProvider(primary=primary, fallback=StubOCRProvider(result=fallback_result))

    result = await provider.extract(sample_pdf_bytes, "upload.pdf", "application/pdf")

    assert result.text == "Recovered locally"
    assert result.confidence == 0.91


@pytest.mark.asyncio
async def test_resilient_ocr_provider_does_not_hide_non_fallback_errors(sample_pdf_bytes) -> None:
    provider = ResilientOCRProvider(
        primary=StubOCRProvider(error=ProcessingError("LOCAL_OCR_DEPENDENCY_MISSING", "missing")),
        fallback=StubOCRProvider(result=OCRResult(text="unused", pages=[])),
    )

    with pytest.raises(ProcessingError) as exc_info:
        await provider.extract(sample_pdf_bytes, "upload.pdf", "application/pdf")

    assert exc_info.value.code == "LOCAL_OCR_DEPENDENCY_MISSING"


@pytest.mark.asyncio
async def test_id_extraction(sample_pdf_bytes) -> None:
    ocr = await MockOCRProvider().extract(sample_pdf_bytes, "id-card.pdf", "application/pdf")
    extracted = IDCardExtractor().extract(ocr)
    assert extracted["name"] == "John Doe"
    assert extracted["document_number"] == "ABCD1234"


@pytest.mark.asyncio
async def test_passport_extraction(sample_pdf_bytes) -> None:
    ocr = await MockOCRProvider().extract(sample_pdf_bytes, "passport.pdf", "application/pdf")
    extracted = PassportExtractor().extract(ocr)
    assert extracted["passport_number"] == "P1234567"
    assert DocumentClassifier().classify(ocr) == DocumentType.PASSPORT


@pytest.mark.asyncio
async def test_driving_license_extraction(sample_pdf_bytes) -> None:
    ocr = await MockOCRProvider().extract(sample_pdf_bytes, "license.pdf", "application/pdf")
    extracted = DrivingLicenseExtractor().extract(ocr)
    assert extracted["license_number"] == "DL-556677"
    assert extracted["vehicle_classes"] == ["LMV", "MCWG"]


@pytest.mark.asyncio
async def test_bank_statement_extraction(sample_pdf_bytes) -> None:
    ocr = await MockOCRProvider().extract(sample_pdf_bytes, "bank.pdf", "application/pdf")
    extracted = BankStatementExtractor().extract(ocr)
    assert extracted["bank_name"] == "Sample Bank"
    assert len(extracted["transactions"]) == 2


@pytest.mark.asyncio
async def test_salary_slip_extraction(sample_pdf_bytes) -> None:
    ocr = await MockOCRProvider().extract(sample_pdf_bytes, "salary.pdf", "application/pdf")
    extracted = SalarySlipExtractor().extract(ocr)
    assert extracted["employee_id"] == "EMP1001"
    assert extracted["net_salary"] == "65000"


def test_id_extraction_with_regex_aliases() -> None:
    ocr = OCRResult(
        text=(
            "IDENTITY CARD\n"
            "Name John Regex\n"
            "Father's Name: Robert Regex\n"
            "D.O.B 12/04/1995\n"
            "Sex M\n"
            "ID No. ZXCV12345\n"
            "Address 77 Lake View Road\n"
        )
    )
    extracted = IDCardExtractor().extract(ocr)
    assert extracted["name"] == "John Regex"
    assert extracted["father_name"] == "Robert Regex"
    assert extracted["document_number"] == "ZXCV12345"
    assert extracted["gender"] == "Male"


def test_bank_statement_extraction_with_regex_aliases() -> None:
    ocr = OCRResult(
        text=(
            "STATEMENT\n"
            "Bank: Regex Bank\n"
            "Customer Name John Holder\n"
            "A/C No 9988776655\n"
            "Type of Account Savings\n"
            "Statement Period 01/01/2024 - 31/01/2024\n"
            "Opening Bal 1000.00\n"
            "Closing Balance 3500.00\n"
            "05/01/2024  Salary Credit  REF001  0.00  2500.00  3500.00  CREDIT\n"
        )
    )
    extracted = BankStatementExtractor().extract(ocr)
    assert extracted["bank_name"] == "Regex Bank"
    assert extracted["account_number"] == "9988776655"
    assert extracted["account_holder"] == "John Holder"
    assert len(extracted["transactions"]) == 1


def test_key_value_model_converts_text_and_structured_fields() -> None:
    model = HeuristicKeyValueModel()

    result = model.transform(
        DocumentType.BANK_STATEMENT,
        raw_text=(
            "BANK MUSCAT\n"
            "SME Current Account Statement\n"
            "Statement Date: 30 Jun 2026\n"
            "CRN\n"
            "12345678\n"
        ),
        extracted_data={
            "bank_name": "Bank Muscat",
            "account_type": "SME Current Account Statement",
            "opening_balance": "50000.00",
            "transactions": [],
        },
    )

    assert result["key_values"]["Bank Muscat"] == "SME Current Account Statement"
    assert result["key_values"]["Statement Date"] == "30 Jun 2026"
    assert result["key_values"]["CRN"] == "12345678"
    assert result["key_values"]["Opening Balance"] == "50000.00"


def test_bank_statement_extraction_with_multiline_ocr_layout() -> None:
    ocr = OCRResult(
        text=(
            "FIRST BANK OF WIKI\n"
            "1425 JAMES ST, PO BOX 4000\n"
            "CHEQUING ACCOUNT STATEMENT\n"
            "VICTORIA BC V8X 3X4\n"
            "1-800-555-5555\n"
            "Page:1 of 1\n"
            "JOHN JONES\n"
            "Statement period\n"
            "Account No.\n"
            "1643 DUNDAS ST W APT 27\n"
            "2003-10-09 to 2003-11-08\n"
            "00005-\n"
            "TORONTO ON M6K 1V2\n"
            "123-456-7\n"
            "Date\n"
            "Description\n"
            "Ref.withdrawals.\n"
            "-\n"
            "Deposits\n"
            "Balance\n"
            "2003-10-08\n"
            "Previous balance\n"
            "0.55\n"
            "2003-10-14\n"
            "Payroll Deposit -HOTEL\n"
            "694.81\n"
            "695.36\n"
            "2003-10-14\n"
            "Web Bill Payment - MASTERCARD\n"
            "9685\n"
            "200.00\n"
            "495.36\n"
            "2003-10-16\n"
            "ATM Withdrawal - INTERAC\n"
            "3990\n"
            "21.25\n"
            "474.11\n"
            "2003-11-08\n"
            "Fees -Monthly\n"
            "5.00\n"
            "-72.47\n"
            "*** Totals ***\n"
            "1,515.63\n"
            "1,442.61\n"
        )
    )
    extracted = BankStatementExtractor().extract(ocr)
    assert extracted["bank_name"] == "First Bank Of Wiki"
    assert extracted["account_holder"] == "John Jones"
    assert extracted["account_number"] == "123-456-7"
    assert extracted["account_type"] == "Chequing"
    assert extracted["statement_start"] == "2003-10-09"
    assert extracted["statement_end"] == "2003-11-08"
    assert extracted["opening_balance"] == "0.55"
    assert extracted["closing_balance"] == "-72.47"
    assert len(extracted["transactions"]) == 4
    assert extracted["transactions"][0]["transaction_type"] == "CREDIT"
    assert extracted["transactions"][0]["credit"] == "694.81"
    assert extracted["transactions"][1]["reference_number"] == "9685"
    assert extracted["transactions"][1]["debit"] == "200.00"
    assert extracted["transactions"][-1]["balance"] == "-72.47"


def test_financial_summary_and_monthly_aggregation() -> None:
    documents = [
        (
            "doc-1",
            {
                "transactions": [
                    {
                        "transaction_date": "2024-01-05",
                        "description": "Amazon",
                        "reference_number": "R1",
                        "debit": Decimal("2500.00"),
                        "credit": None,
                        "balance": Decimal("100.00"),
                        "transaction_type": "DEBIT",
                    },
                    {
                        "transaction_date": "2024-01-06",
                        "description": "Salary",
                        "reference_number": "R2",
                        "debit": None,
                        "credit": Decimal("85000.00"),
                        "balance": Decimal("85100.00"),
                        "transaction_type": "CREDIT",
                    },
                ]
            },
        )
    ]
    service = FinancialAnalysisService()
    summary = service.summarize(documents)
    assert summary.total_income == Decimal("85000.00")
    assert summary.total_expenses == Decimal("2500.00")
    assert summary.net_cash_flow == Decimal("82500.00")

    monthly = service.monthly_summary(documents)
    assert monthly.items[0].month == "2024-01"
    assert monthly.items[0].income == Decimal("85000.00")
    assert monthly.items[0].expenses == Decimal("2500.00")

