from app.schemas.ocr import OCRPage, OCRResult
from app.services.ocr.base import OCRProvider


class MockOCRProvider(OCRProvider):
    async def extract(self, file_bytes: bytes, filename: str, content_type: str) -> OCRResult:
        lower_name = filename.lower()
        if not file_bytes:
            return OCRResult(text="", confidence=0.0, pages=[])
        if "fail" in lower_name:
            raise RuntimeError("Mock OCR failure")
        if "malformed" in lower_name:
            return OCRResult(text="", confidence=None, pages=[], raw_response={"unexpected": True})

        samples = {
            "id": "ID CARD\nName: John Doe\nDOB: 12/04/1995\nGender: Male\nDocument Number: ABCD1234\nAddress: 12 Main Street, Springfield\nIssue Date: 01/01/2020\nExpiry Date: 01/01/2030",
            "passport": "PASSPORT\nFull Name: Jane Citizen\nPassport Number: P1234567\nNationality: Indian\nDate of Birth: 04/09/1990\nGender: Female\nDate of Issue: 03/03/2021\nDate of Expiry: 03/03/2031\nPlace of Birth: Mumbai\nPlace of Issue: Delhi",
            "license": "DRIVING LICENSE\nName: Alex Driver\nDOB: 15/05/1988\nLicense Number: DL-556677\nAddress: 8 Road Avenue\nIssue Date: 10/10/2022\nExpiry Date: 10/10/2032\nVehicle Classes: LMV, MCWG",
            "bank": "BANK STATEMENT\nBank Name: Sample Bank\nAccount Holder: John Doe\nAccount Number: 123456789012\nAccount Type: Savings\nStatement Period: 01/01/2024 - 31/01/2024\nOpening Balance: 1000.00\nClosing Balance: 83500.00\n05/01/2024 | Amazon Purchase | REF123 | 2500.00 |  | -1500.00 | DEBIT\n06/01/2024 | Salary Credit | REF124 |  | 85000.00 | 83500.00 | CREDIT",
            "salary": "SALARY SLIP\nEmployee Name: John Doe\nEmployee ID: EMP1001\nEmployer Name: Acme Corp\nPay Period: 31/01/2024\nBasic Salary: 60000\nAllowances: 10000\nDeductions: 5000\nGross Salary: 70000\nNet Salary: 65000\nTax: 4000\nOther Deductions: 1000",
        }

        key = next((candidate for candidate in samples if candidate in lower_name), "id")
        text = samples[key]
        confidence = 0.45 if "low-confidence" in lower_name else 0.96
        return OCRResult(
            text=text,
            confidence=confidence,
            pages=[OCRPage(page_number=1, text=text, confidence=confidence)],
            raw_response={"provider": "mock", "content_type": content_type},
        )

