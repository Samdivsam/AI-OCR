import { formatDate, maskValue, prettifyKey } from "@/lib/format";

type Props = {
  extraction: Record<string, unknown>;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function renderScalar(key: string, value: unknown) {
  if (value === null || value === undefined || value === "") {
    return <span>—</span>;
  }

  if (typeof value === "string" && (key === "ocr_text_preview" || key === "raw_text_preview" || key === "extraction_warning")) {
    return <pre className="whitespace-pre-wrap rounded-lg bg-slate-100 p-3 text-xs text-slate-700">{value}</pre>;
  }

  const maybeDate = typeof value === "string" && /^\d{4}-\d{2}-\d{2}/.test(value) ? formatDate(value) : maskValue(value, key);
  return <span>{maybeDate}</span>;
}

function TransactionTable({ items }: { items: Record<string, unknown>[] }) {
  const columns = ["transaction_date", "description", "reference_number", "debit", "credit", "balance", "transaction_type"];

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((column) => (
              <th key={column} className="px-3 py-2 text-left font-medium text-slate-500">
                {prettifyKey(column)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {items.map((item, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td key={column} className="px-3 py-2 text-slate-700">
                  {renderScalar(column, item[column])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function NestedFields({ data }: { data: Record<string, unknown> }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {Object.entries(data).map(([nestedKey, nestedValue]) => (
        <div key={nestedKey} className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{prettifyKey(nestedKey)}</p>
          <div className="mt-2 text-sm text-slate-900">{renderValue(nestedKey, nestedValue)}</div>
        </div>
      ))}
    </div>
  );
}

function renderValue(key: string, value: unknown): React.ReactNode {
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span>—</span>;
    }

    if (key === "transactions" && value.every(isRecord)) {
      return <TransactionTable items={value} />;
    }

    if (value.every((item) => typeof item !== "object" || item === null)) {
      return (
        <div className="flex flex-wrap gap-2">
          {value.map((item, index) => (
            <span key={index} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
              {maskValue(item, key)}
            </span>
          ))}
        </div>
      );
    }

    return (
      <div className="space-y-2">
        {value.map((item, index) => (
          <div key={index} className="rounded-lg bg-slate-50 p-3">
            {isRecord(item) ? <NestedFields data={item} /> : renderScalar(key, item)}
          </div>
        ))}
      </div>
    );
  }

  if (isRecord(value)) {
    return <NestedFields data={value} />;
  }

  return renderScalar(key, value);
}

export function FieldList({ extraction }: Props) {
  return (
    <div className="grid gap-4">
      {typeof extraction.key_values === "object" && extraction.key_values !== null && Object.keys(extraction.key_values as Record<string, unknown>).length > 0 && (
        <div className="rounded-xl bg-blue-50 p-4 ring-1 ring-blue-200">
          <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-blue-700">OCR Detected Fields</p>
          <div className="grid gap-2 sm:grid-cols-2">
            {Object.entries(extraction.key_values as Record<string, unknown>).map(([key, value]) => (
              <div key={key} className="rounded-lg bg-white p-3">
                <p className="text-xs font-medium text-slate-500">{key}</p>
                <p className="mt-1 text-sm font-medium text-slate-900">{String(value)}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {Object.entries(extraction).filter(([key]) => key !== "key_values").map(([key, value]) => (
        <div key={key} className="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm font-medium text-slate-500">{prettifyKey(key)}</p>
          <div className="mt-2 text-sm text-slate-900">{renderValue(key, value)}</div>
        </div>
      ))}
    </div>
  );
}

