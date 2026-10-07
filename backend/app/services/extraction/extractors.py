import re
from decimal import Decimal
from typing import Any

from app.schemas.bank_statement import BankStatementExtraction, BankTransaction
from app.schemas.driving_license import DrivingLicenseExtraction
from app.schemas.id_card import IDCardExtraction
from app.schemas.ocr import OCRResult
from app.schemas.passport import PassportExtraction
from app.schemas.salary_slip import SalarySlipExtraction
from app.services.extraction.base import DocumentExtractor
from app.services.extraction.helpers import (
    extract_all_dates,
    extract_first_date,
    extract_labeled_value,
    extract_regex_value,
    extract_key_value_pairs,
    normalize_ocr_text,
    normalize_gender,
    parse_date,
    parse_decimal,
)

COMMON_STOP_ALIASES = [
    r"name",
    r"full\s*name",
    r"father'?s\s*name",
    r"date\s*of\s*birth",
    r"dob",
    r"birth\s*date",
    r"gender",
    r"sex",
    r"document\s*(?:number|no\.?|#)",
    r"id\s*(?:number|no\.?|#)",
    r"passport\s*(?:number|no\.?|#)",
    r"license\s*(?:number|no\.?|#)",
    r"licence\s*(?:number|no\.?|#)",
    r"account\s*(?:number|no\.?|#)",
    r"a/?c\s*(?:number|no\.?)",
    r"account\s*holder",
    r"address",
    r"addr(?:ess)?",
    r"issue\s*date",
    r"expiry\s*date",
    r"date\s*of\s*issue",
    r"date\s*of\s*expiry",
    r"nationality",
    r"place\s*of\s*birth",
    r"place\s*of\s*issue",
    r"employee\s*name",
    r"employee\s*id",
    r"employer\s*name",
    r"basic\s*salary",
    r"gross\s*salary",
    r"net\s*salary",
    r"tax",
    r"statement\s*period",
    r"opening\s*balance",
    r"closing\s*balance",
]

NAME_ALIASES = [r"full\s*name", r"name\s*of\s*holder", r"name"]
FATHER_NAME_ALIASES = [r"father'?s\s*name", r"parent'?s\s*name", r"guardian'?s\s*name", r"s/o", r"d/o", r"c/o"]
DOB_ALIASES = [r"date\s*of\s*birth", r"birth\s*date", r"d\.?o\.?b\.?", r"dob"]
GENDER_ALIASES = [r"gender", r"sex"]
ADDRESS_ALIASES = [r"address", r"addr(?:ess)?"]
ISSUE_DATE_ALIASES = [r"issue\s*date", r"date\s*of\s*issue", r"issued\s*on"]
EXPIRY_DATE_ALIASES = [r"expiry\s*date", r"date\s*of\s*expiry", r"valid\s*till", r"expires?\s*on"]


class IDCardExtractor(DocumentExtractor):
    def extract(self, ocr_result: OCRResult) -> dict[str, Any]:
        dates = extract_all_dates(ocr_result.text)
        model = IDCardExtraction(
            name=extract_labeled_value(ocr_result.text, NAME_ALIASES, stop_aliases=COMMON_STOP_ALIASES),
            father_name=extract_labeled_value(ocr_result.text, FATHER_NAME_ALIASES, stop_aliases=COMMON_STOP_ALIASES),
            date_of_birth=parse_date(extract_labeled_value(ocr_result.text, DOB_ALIASES)) or (dates[0] if dates else None),
            gender=normalize_gender(extract_labeled_value(ocr_result.text, GENDER_ALIASES)),
            document_number=extract_regex_value(
                ocr_result.text,
                [
                    r"^\s*ID\s*No\.?\s*[:#-]?\s*([A-Z0-9\-/]{4,})\s*$",
                    r"^\s*Document\s*(?:Number|No\.?)\s*[:#-]?\s*([A-Z0-9\-/]{4,})\s*$",
                    r"^\s*Card\s*(?:Number|No\.?)\s*[:#-]?\s*([A-Z0-9\-/]{4,})\s*$",
                ],
            )
            or extract_labeled_value(
                ocr_result.text,
                [r"document\s*(?:number|no\.?|#)", r"id\s*(?:number|no\.?|#)", r"card\s*(?:number|no\.?|#)", r"identity\s*(?:number|no\.?)"],
            ),
            address=extract_labeled_value(ocr_result.text, ADDRESS_ALIASES, multiline=True, stop_aliases=COMMON_STOP_ALIASES),
            issue_date=parse_date(extract_labeled_value(ocr_result.text, ISSUE_DATE_ALIASES)) or (dates[1] if len(dates) > 1 else None),
            expiry_date=parse_date(extract_labeled_value(ocr_result.text, EXPIRY_DATE_ALIASES)) or (dates[-1] if len(dates) > 2 else None),
            key_values=extract_key_value_pairs(ocr_result.text),
        )
        return model.model_dump(mode="json")


class PassportExtractor(DocumentExtractor):
    def extract(self, ocr_result: OCRResult) -> dict[str, Any]:
        dates = extract_all_dates(ocr_result.text)
        model = PassportExtraction(
            full_name=extract_labeled_value(ocr_result.text, [r"full\s*name", r"name", r"surname\s*and\s*given\s*name"], stop_aliases=COMMON_STOP_ALIASES),
            passport_number=extract_labeled_value(
                ocr_result.text,
                [r"passport\s*(?:number|no\.?|#)", r"document\s*(?:number|no\.?|#)", r"passport\s*no"],
            ) or extract_regex_value(ocr_result.text, [r"\b([A-Z]\d{6,9})\b"]),
            nationality=extract_labeled_value(ocr_result.text, [r"nationality", r"country"]),
            date_of_birth=parse_date(extract_labeled_value(ocr_result.text, DOB_ALIASES)) or (dates[0] if dates else None),
            gender=normalize_gender(extract_labeled_value(ocr_result.text, GENDER_ALIASES)),
            date_of_issue=parse_date(extract_labeled_value(ocr_result.text, ISSUE_DATE_ALIASES)) or (dates[1] if len(dates) > 1 else None),
            date_of_expiry=parse_date(extract_labeled_value(ocr_result.text, EXPIRY_DATE_ALIASES)) or (dates[-1] if len(dates) > 2 else None),
            place_of_birth=extract_labeled_value(ocr_result.text, [r"place\s*of\s*birth", r"birth\s*place"]),
            place_of_issue=extract_labeled_value(ocr_result.text, [r"place\s*of\s*issue", r"issue\s*place"]),
            key_values=extract_key_value_pairs(ocr_result.text),
        )
        return model.model_dump(mode="json")


class DrivingLicenseExtractor(DocumentExtractor):
    def extract(self, ocr_result: OCRResult) -> dict[str, Any]:
        dates = extract_all_dates(ocr_result.text)
        vehicle_classes = extract_labeled_value(
            ocr_result.text,
            [r"vehicle\s*classes", r"class(?:es)?\s*of\s*vehicle", r"vehicle\s*class"],
        )
        model = DrivingLicenseExtraction(
            name=extract_labeled_value(ocr_result.text, NAME_ALIASES, stop_aliases=COMMON_STOP_ALIASES),
            father_name=extract_labeled_value(ocr_result.text, FATHER_NAME_ALIASES, stop_aliases=COMMON_STOP_ALIASES),
            date_of_birth=parse_date(extract_labeled_value(ocr_result.text, DOB_ALIASES)) or (dates[0] if dates else None),
            license_number=extract_labeled_value(
                ocr_result.text,
                [r"license\s*(?:number|no\.?|#)", r"licence\s*(?:number|no\.?|#)", r"dl\s*(?:number|no\.?)"],
            ) or extract_regex_value(ocr_result.text, [r"\b([A-Z]{1,4}[\-/]?[A-Z0-9]{4,20})\b"]),
            address=extract_labeled_value(ocr_result.text, ADDRESS_ALIASES, multiline=True, stop_aliases=COMMON_STOP_ALIASES),
            issue_date=parse_date(extract_labeled_value(ocr_result.text, ISSUE_DATE_ALIASES)) or (dates[1] if len(dates) > 1 else None),
            expiry_date=parse_date(extract_labeled_value(ocr_result.text, EXPIRY_DATE_ALIASES)) or (dates[-1] if len(dates) > 2 else None),
            vehicle_classes=[item.strip() for item in vehicle_classes.split(",")] if vehicle_classes else [],
            key_values=extract_key_value_pairs(ocr_result.text),
        )
        return model.model_dump(mode="json")


class SalarySlipExtractor(DocumentExtractor):
    def extract(self, ocr_result: OCRResult) -> dict[str, Any]:
        model = SalarySlipExtraction(
            employee_name=extract_labeled_value(ocr_result.text, [r"employee\s*name", r"emp(?:loyee)?\s*name", r"name"], stop_aliases=COMMON_STOP_ALIASES),
            employee_id=extract_labeled_value(ocr_result.text, [r"employee\s*id", r"emp(?:loyee)?\s*id", r"staff\s*id", r"id\s*number"]),
            employer_name=extract_labeled_value(ocr_result.text, [r"employer\s*name", r"company\s*name", r"organization\s*name"]),
            pay_period=parse_date(extract_labeled_value(ocr_result.text, [r"pay\s*period", r"salary\s*month", r"month", r"period"])),
            basic_salary=parse_decimal(extract_labeled_value(ocr_result.text, [r"basic\s*salary", r"basic\s*pay", r"basic"])),
            allowances=parse_decimal(extract_labeled_value(ocr_result.text, [r"allowances?", r"allowance"])),
            deductions=parse_decimal(extract_labeled_value(ocr_result.text, [r"deductions?", r"total\s*deductions?"])),
            gross_salary=parse_decimal(extract_labeled_value(ocr_result.text, [r"gross\s*salary", r"gross\s*pay", r"gross"])),
            net_salary=parse_decimal(extract_labeled_value(ocr_result.text, [r"net\s*salary", r"net\s*pay", r"take\s*home"])),
            tax=parse_decimal(extract_labeled_value(ocr_result.text, [r"tax", r"income\s*tax", r"tds"])),
            other_deductions=parse_decimal(extract_labeled_value(ocr_result.text, [r"other\s*deductions?", r"misc(?:ellaneous)?\s*deductions?"])),
            key_values=extract_key_value_pairs(ocr_result.text),
        )
        return model.model_dump(mode="json")


class BankStatementExtractor(DocumentExtractor):
    date_pattern_text = r"(?:\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})"
    transaction_pattern = re.compile(
        rf"(?P<date>{date_pattern_text})\s*(?:\||\s{{2,}})\s*(?P<description>[^|\n]+?)\s*(?:\||\s{{2,}})\s*(?P<reference>[^|\n]*)\s*(?:\||\s{{2,}})\s*(?P<debit>[^|\n]*)\s*(?:\||\s{{2,}})\s*(?P<credit>[^|\n]*)\s*(?:\||\s{{2,}})\s*(?P<balance>[^|\n]*)\s*(?:\||\s{{2,}})\s*(?P<type>[A-Z ]+)?",
        re.IGNORECASE,
    )
    date_line_pattern = re.compile(rf"^{date_pattern_text}$")
    date_range_pattern = re.compile(
        rf"(?P<start>{date_pattern_text})\s*(?:to|through|until|-|–|—)\s*(?P<end>{date_pattern_text})",
        re.IGNORECASE,
    )
    amount_pattern = re.compile(r"^-?(?:\d{1,3}(?:,\d{3})*|\d+)\.\d{2}$")
    account_type_pattern = re.compile(r"\b(CHEQUING|CHECKING|SAVINGS|CURRENT)\b", re.IGNORECASE)

    credit_keywords = ("deposit", "refund", "credit", "salary", "payroll", "interest", "from savings", "transfer -from")
    debit_keywords = ("withdrawal", "payment", "purchase", "fee", "cheque", "check", "mortgage", "debit", "transfer -to")

    def extract(self, ocr_result: OCRResult) -> dict[str, Any]:
        normalized_text = normalize_ocr_text(ocr_result.text)
        lines = [line.strip() for line in normalized_text.splitlines() if line.strip()]
        transactions, inferred_opening_balance = self._extract_transactions(normalized_text, lines)
        start_date, end_date = self._extract_statement_period(normalized_text, transactions)
        closing_balance = parse_decimal(
            extract_labeled_value(normalized_text, [r"closing\s*balance", r"closing\s*bal(?:ance)?", r"available\s*balance"])
        ) or next((tx.balance for tx in reversed(transactions) if tx.balance is not None), None)

        model = BankStatementExtraction(
            bank_name=extract_regex_value(
                normalized_text,
                [
                    r"^\s*Bank\s*[:#-]\s*(.+?)\s*$",
                    r"^\s*Bank\s*Name\s*[:#-]?\s*(.+?)\s*$",
                    r"^\s*Name\s*of\s*Bank\s*[:#-]?\s*(.+?)\s*$",
                ],
            )
            or extract_labeled_value(normalized_text, [r"bank\s*name", r"name\s*of\s*bank"])
            or self._infer_bank_name(lines),
            account_holder=extract_labeled_value(normalized_text, [r"account\s*holder", r"customer\s*name", r"name"], stop_aliases=COMMON_STOP_ALIASES)
            or self._infer_account_holder(lines),
            account_number=extract_labeled_value(
                normalized_text,
                [r"account\s*(?:number|no\.?|#)", r"a/?c\s*(?:number|no\.?)", r"acct\s*(?:number|no\.?)"],
            )
            or self._infer_account_number(lines),
            account_type=extract_labeled_value(normalized_text, [r"account\s*type", r"type\s*of\s*account"])
            or self._infer_account_type(lines),
            statement_start=start_date,
            statement_end=end_date,
            opening_balance=parse_decimal(extract_labeled_value(normalized_text, [r"opening\s*balance", r"opening\s*bal(?:ance)?"]))
            or inferred_opening_balance,
            closing_balance=closing_balance,
            transactions=transactions,
            key_values=extract_key_value_pairs(normalized_text),
        )
        return model.model_dump(mode="json")

    def _extract_statement_period(self, text: str, transactions: list[BankTransaction]) -> tuple[Any, Any]:
        period = extract_labeled_value(text, [r"statement\s*period", r"period", r"statement\s*range"], multiline=True)
        if period:
            parsed = self._parse_date_range(period)
            if parsed != (None, None):
                return parsed

        range_match = self.date_range_pattern.search(text)
        if range_match:
            return parse_date(range_match.group("start")), parse_date(range_match.group("end"))

        dated_transactions = [tx.transaction_date for tx in transactions if tx.transaction_date is not None]
        return (dated_transactions[0], dated_transactions[-1]) if dated_transactions else (None, None)

    def _parse_date_range(self, value: str) -> tuple[Any, Any]:
        match = self.date_range_pattern.search(value)
        if not match:
            return None, None
        return parse_date(match.group("start")), parse_date(match.group("end"))

    def _extract_transactions(self, text: str, lines: list[str]) -> tuple[list[BankTransaction], Decimal | None]:
        inline_transactions = self._extract_inline_transactions(text)
        stacked_transactions, inferred_opening_balance = self._extract_stacked_transactions(lines)
        if len(stacked_transactions) > len(inline_transactions):
            return stacked_transactions, inferred_opening_balance
        return inline_transactions, inferred_opening_balance

    def _extract_inline_transactions(self, text: str) -> list[BankTransaction]:
        transactions: list[BankTransaction] = []
        for match in self.transaction_pattern.finditer(text):
            debit = parse_decimal(match.group("debit"))
            credit = parse_decimal(match.group("credit"))
            balance = parse_decimal(match.group("balance"))
            description = match.group("description").strip()
            amount = credit or debit
            transaction_type = (match.group("type") or "").strip().upper() or self._infer_transaction_direction(description, None, balance, amount)
            tx = BankTransaction(
                transaction_date=parse_date(match.group("date")),
                description=description,
                reference_number=match.group("reference").strip() or None,
                debit=debit,
                credit=credit,
                balance=balance,
                transaction_type=transaction_type,
            )
            transactions.append(tx)
        return transactions

    def _extract_stacked_transactions(self, lines: list[str]) -> tuple[list[BankTransaction], Decimal | None]:
        blocks: list[tuple[str, list[str]]] = []
        current_date: str | None = None
        current_lines: list[str] = []

        for line in lines:
            if self.date_line_pattern.fullmatch(line):
                if current_date is not None:
                    blocks.append((current_date, current_lines))
                current_date = line
                current_lines = []
                continue
            if current_date is None:
                continue
            if line.lower().startswith("*** totals"):
                break
            current_lines.append(line)

        if current_date is not None:
            blocks.append((current_date, current_lines))

        transactions: list[BankTransaction] = []
        opening_balance: Decimal | None = None
        previous_balance: Decimal | None = None

        for date_text, block_lines in blocks:
            tx = self._build_transaction_from_block(date_text, block_lines, previous_balance)
            if tx is None:
                continue
            description = (tx.description or "").lower()
            if "previous balance" in description:
                opening_balance = tx.balance or tx.credit or tx.debit
                previous_balance = opening_balance
                continue
            if tx.balance is not None:
                previous_balance = tx.balance
            transactions.append(tx)

        return transactions, opening_balance

    def _build_transaction_from_block(
        self,
        date_text: str,
        block_lines: list[str],
        previous_balance: Decimal | None,
    ) -> BankTransaction | None:
        description_parts: list[str] = []
        amounts: list[Decimal] = []
        reference_number: str | None = None

        for line in block_lines:
            if self.amount_pattern.fullmatch(line):
                amount = parse_decimal(line)
                if amount is not None:
                    amounts.append(amount)
                continue
            if reference_number is None and self._is_reference_candidate(line):
                reference_number = line
                continue
            description_parts.append(line)

        description = " ".join(description_parts).strip()
        if not description and not amounts:
            return None

        lower_description = description.lower()
        if "previous balance" in lower_description:
            return BankTransaction(
                transaction_date=parse_date(date_text),
                description=description,
                reference_number=reference_number,
                balance=amounts[-1] if amounts else previous_balance,
                transaction_type="OPENING",
            )

        amount = amounts[0] if len(amounts) >= 2 else None
        balance = amounts[-1] if len(amounts) >= 2 else (amounts[0] if amounts else previous_balance)
        transaction_type = self._infer_transaction_direction(description, previous_balance, balance, amount)
        debit = credit = None
        if amount is not None:
            if transaction_type == "CREDIT":
                credit = amount
            elif transaction_type == "DEBIT":
                debit = amount

        return BankTransaction(
            transaction_date=parse_date(date_text),
            description=description,
            reference_number=reference_number,
            debit=debit,
            credit=credit,
            balance=balance,
            transaction_type=transaction_type,
        )

    def _is_reference_candidate(self, line: str) -> bool:
        return bool(re.fullmatch(r"[A-Z0-9-]{3,}", line)) and parse_date(line) is None and not self.amount_pattern.fullmatch(line)

    def _infer_transaction_direction(
        self,
        description: str,
        previous_balance: Decimal | None,
        balance: Decimal | None,
        amount: Decimal | None,
    ) -> str | None:
        normalized = description.lower()
        if any(keyword in normalized for keyword in self.credit_keywords):
            return "CREDIT"
        if any(keyword in normalized for keyword in self.debit_keywords):
            return "DEBIT"
        if previous_balance is not None and balance is not None and amount is not None:
            if balance > previous_balance:
                return "CREDIT"
            if balance < previous_balance:
                return "DEBIT"
        return None

    def _infer_bank_name(self, lines: list[str]) -> str | None:
        for line in lines[:8]:
            upper = line.upper()
            if "BANK" in upper and "STATEMENT" not in upper and "ACCOUNT" not in upper:
                return line.title() if line.isupper() else line
        return None

    def _infer_account_holder(self, lines: list[str]) -> str | None:
        for line in lines[:20]:
            upper = line.upper()
            if any(char.isdigit() for char in line):
                continue
            if any(token in upper for token in ["BANK", "ACCOUNT", "STATEMENT", "PAGE", "DATE", "DESCRIPTION", "BALANCE", "WITHDRAWALS", "DEPOSITS", "TOTALS"]):
                continue
            words = [word for word in re.split(r"\s+", line) if word]
            if 2 <= len(words) <= 4 and all(re.fullmatch(r"[A-Z][A-Z'&.-]*", word) for word in words):
                return line.title() if line.isupper() else line
        return None

    def _infer_account_number(self, lines: list[str]) -> str | None:
        label_pattern = re.compile(r"account\s*(?:number|no\.?|#)|a/?c\s*(?:number|no\.?)|acct\s*(?:number|no\.?)", re.IGNORECASE)
        label_indexes = [index for index, line in enumerate(lines) if label_pattern.search(line)]
        search_indexes = label_indexes or list(range(min(len(lines), 12)))

        best_candidate: str | None = None
        best_score = -1
        for index in search_indexes:
            for candidate in lines[index + 1 : index + 8]:
                score = self._score_account_candidate(candidate)
                if score > best_score:
                    best_score = score
                    best_candidate = candidate
        return best_candidate

    def _score_account_candidate(self, candidate: str) -> int:
        if parse_date(candidate) is not None or self.amount_pattern.fullmatch(candidate):
            return -1
        if any(char.isalpha() for char in candidate) or "." in candidate:
            return -1
        digit_count = sum(char.isdigit() for char in candidate)
        if digit_count < 5:
            return -1
        score = digit_count
        if "-" in candidate and not candidate.endswith("-"):
            score += 2
        if candidate.endswith("-"):
            score -= 3
        if candidate.startswith("1-800"):
            score -= 5
        return score

    def _infer_account_type(self, lines: list[str]) -> str | None:
        for line in lines[:10]:
            match = self.account_type_pattern.search(line)
            if match:
                return match.group(1).title()
        return None


class GenericExtractor(DocumentExtractor):
    def extract(self, ocr_result: OCRResult) -> dict[str, Any]:
        return {"raw_text_preview": ocr_result.text[:500]}

