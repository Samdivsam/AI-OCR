"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { FieldList } from "@/components/field-list";
import { api } from "@/lib/api";
import type { DocumentItem, ExtractionResponse } from "@/types/api";

export default function DocumentDetailsPage() {
  const params = useParams<{ id: string }>();
  const documentId = params.id;
  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [extraction, setExtraction] = useState<ExtractionResponse | null>(null);

  useEffect(() => {
    api.get<DocumentItem>(`/documents/${documentId}`).then(setDocument).catch(() => undefined);
    api.get<ExtractionResponse>(`/documents/${documentId}/extraction`).then(setExtraction).catch(() => undefined);
  }, [documentId]);

  return (
    <AppShell title="Document Details" subtitle="Review structured extracted fields with masked sensitive values.">
      <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <p className="text-sm text-slate-500">Document Type</p>
            <p className="mt-1 font-medium">{document?.document_type ?? "—"}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Status</p>
            <p className="mt-1 font-medium">{document?.status ?? "—"}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Confidence</p>
            <p className="mt-1 font-medium">{extraction?.confidence ?? "N/A"}</p>
          </div>
        </div>
      </div>
      <div className="mt-6">{extraction ? <FieldList extraction={extraction.extraction} /> : null}</div>
    </AppShell>
  );
}

