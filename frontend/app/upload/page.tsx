"use client";

import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { FieldList } from "@/components/field-list";
import { api } from "@/lib/api";
import { DOCUMENT_TYPES, type DocumentType, type ExtractionResponse } from "@/types/api";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<DocumentType | "AUTO">("AUTO");
  const [status, setStatus] = useState("Idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractionResponse | null>(null);

  const upload = async () => {
    if (!file) return;
    setStatus("Uploading");
    setError(null);
    setResult(null);
    try {
      setStatus("Processing OCR");
      const response = await api.upload<ExtractionResponse>(
        "/documents",
        file,
        documentType === "AUTO" ? undefined : documentType,
      );
      setResult(response);
      setStatus("Completed");
    } catch (err) {
      setStatus("Failed");
      setError(err instanceof Error ? err.message : "Upload failed.");
    }
  };

  return (
    <AppShell title="Upload Document" subtitle="Upload PDF, PNG, or JPEG files for OCR extraction. Original files are processed temporarily only.">
      <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <label className="mb-3 block text-sm font-medium text-slate-600">Document type</label>
        <select
          value={documentType}
          onChange={(event) => setDocumentType(event.target.value as DocumentType | "AUTO")}
          className="mb-4 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-brand-500"
        >
          <option value="AUTO">Auto detect</option>
          {DOCUMENT_TYPES.map((type) => (
            <option key={type} value={type}>
              {type.replaceAll("_", " ")}
            </option>
          ))}
        </select>
        <input
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          className="block w-full rounded-xl border border-dashed border-slate-300 p-4"
        />
        <div className="mt-4 flex items-center gap-4">
          <button
            type="button"
            onClick={upload}
            disabled={!file}
            className="rounded-xl bg-brand-600 px-5 py-3 font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            Upload & Process
          </button>
          <span className="text-sm text-slate-600">Status: {status}</span>
        </div>
        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
      </div>

      {result ? (
        <div className="mt-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">{result.document_type}</span>
            <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">{result.status}</span>
            <span className="text-sm text-slate-500">Confidence: {result.confidence ?? "N/A"}</span>
          </div>
          <FieldList extraction={result.extraction} />
        </div>
      ) : null}
    </AppShell>
  );
}

