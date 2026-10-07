export type User = {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type DocumentStatus = "PROCESSING" | "COMPLETED" | "FAILED";
export type DocumentType =
  | "ID_CARD"
  | "PASSPORT"
  | "DRIVING_LICENSE"
  | "BANK_STATEMENT"
  | "SALARY_SLIP"
  | "OTHER";

export const DOCUMENT_TYPES: DocumentType[] = [
  "ID_CARD",
  "PASSPORT",
  "DRIVING_LICENSE",
  "BANK_STATEMENT",
  "SALARY_SLIP",
  "OTHER",
];

export type DocumentItem = {
  id: string;
  document_type: DocumentType;
  original_filename: string;
  mime_type: string;
  file_size: number;
  status: DocumentStatus;
  created_at: string;
  processed_at?: string | null;
};

export type DocumentListResponse = {
  items: DocumentItem[];
  total: number;
};

export type ExtractionResponse = {
  document_id: string;
  document_type: DocumentType;
  status: DocumentStatus;
  extraction: Record<string, unknown>;
  confidence?: number | null;
  extraction_version?: string | null;
};

export type DashboardSummary = {
  total_documents: number;
  by_type: Record<string, number>;
  recent_documents: DocumentItem[];
};

export type FinancialSummary = {
  total_income: string;
  total_expenses: string;
  net_cash_flow: string;
  transaction_count: number;
};

export type FinancialTransaction = {
  document_id: string;
  transaction_date?: string | null;
  description?: string | null;
  reference_number?: string | null;
  debit?: string | null;
  credit?: string | null;
  balance?: string | null;
  transaction_type?: string | null;
};

export type MonthlySummary = {
  items: Array<{
    month: string;
    income: string;
    expenses: string;
    net: string;
  }>;
};

