from app.schemas.common import DocumentType
from app.schemas.ocr import OCRResult


class DocumentClassifier:
    def classify(self, ocr_result: OCRResult) -> DocumentType:
        text = ocr_result.text.upper()
        if any(keyword in text for keyword in ["BANK STATEMENT", "ACCOUNT NUMBER", "OPENING BALANCE", "CLOSING BALANCE", "ACCOUNT STATEMENT", "BALANCE", "DEPOSIT"]):
            return DocumentType.BANK_STATEMENT
        if any(keyword in text for keyword in ["PASSPORT", "PASSPORT NUMBER", "NATIONALITY"]):
            return DocumentType.PASSPORT
        if any(keyword in text for keyword in ["DRIVING LICENSE", "LICENCE NUMBER", "LICENSE NUMBER", "VEHICLE CLASSES"]):
            return DocumentType.DRIVING_LICENSE
        if any(keyword in text for keyword in ["SALARY SLIP", "NET SALARY", "EMPLOYEE ID", "GROSS SALARY"]):
            return DocumentType.SALARY_SLIP
        if any(keyword in text for keyword in ["ID CARD", "DOCUMENT NUMBER", "DOB", "DATE OF BIRTH"]):
            return DocumentType.ID_CARD
        return DocumentType.OTHER

