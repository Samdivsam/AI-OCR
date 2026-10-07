export function maskValue(value: unknown, key?: string): string {
  if (value === null || value === undefined) return "—";
  const text = String(value);
  const sensitive = ["account_number", "document_number", "passport_number", "license_number", "address"];
  if (key && sensitive.includes(key) && text.length > 4) {
    if (key === "address") {
      return "********";
    }
    return `${"*".repeat(Math.max(0, text.length - 4))}${text.slice(-4)}`;
  }
  return text;
}

export function prettifyKey(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString();
}

