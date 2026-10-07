"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { DocumentListResponse } from "@/types/api";

export default function DocumentsPage() {
  const [data, setData] = useState<DocumentListResponse | null>(null);

  useEffect(() => {
    api.get<DocumentListResponse>("/documents").then(setData).catch(() => undefined);
  }, []);

  return (
    <AppShell title="Documents" subtitle="View processed documents and open extracted details.">
      <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-slate-500">
            <tr>
              <th className="px-6 py-4 font-medium">Document Type</th>
              <th className="px-6 py-4 font-medium">File</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Processed</th>
              <th className="px-6 py-4 font-medium">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {data?.items.map((doc) => (
              <tr key={doc.id}>
                <td className="px-6 py-4">{doc.document_type}</td>
                <td className="px-6 py-4">{doc.original_filename}</td>
                <td className="px-6 py-4">{doc.status}</td>
                <td className="px-6 py-4">{formatDate(doc.processed_at ?? doc.created_at)}</td>
                <td className="px-6 py-4">
                  <Link href={`/documents/${doc.id}`} className="font-medium text-brand-600">
                    View details
                  </Link>
                </td>
              </tr>
            ))}
            {!data?.items.length ? (
              <tr>
                <td className="px-6 py-8 text-slate-500" colSpan={5}>
                  No documents available yet.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}

