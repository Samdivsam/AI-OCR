from app.schemas.common import DocumentType
from app.services.extraction.base import DocumentExtractor
from app.services.extraction.extractors import (
    BankStatementExtractor,
    DrivingLicenseExtractor,
    GenericExtractor,
    IDCardExtractor,
    PassportExtractor,
    SalarySlipExtractor,
)


class ExtractorRegistry:
    def __init__(self) -> None:
        self._extractors: dict[DocumentType, DocumentExtractor] = {
            DocumentType.ID_CARD: IDCardExtractor(),
            DocumentType.PASSPORT: PassportExtractor(),
            DocumentType.DRIVING_LICENSE: DrivingLicenseExtractor(),
            DocumentType.BANK_STATEMENT: BankStatementExtractor(),
            DocumentType.SALARY_SLIP: SalarySlipExtractor(),
            DocumentType.OTHER: GenericExtractor(),
        }

    def get(self, document_type: DocumentType) -> DocumentExtractor:
        return self._extractors[document_type]

