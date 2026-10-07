"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/stat-card";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { DashboardSummary, FinancialSummary } from "@/types/api";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [financial, setFinancial] = useState<FinancialSummary | null>(null);

  useEffect(() => {
    api.get<DashboardSummary>("/documents/dashboard").then(setSummary).catch(() => undefined);
    api.get<FinancialSummary>("/financial/summary").then(setFinancial).catch(() => undefined);
  }, []);

  return (
    <AppShell title="Dashboard" subtitle="Overview of processed documents and basic financial insight foundations.">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Documents" value={summary?.total_documents ?? 0} />
        <StatCard label="Bank Statements" value={summary?.by_type?.BANK_STATEMENT ?? 0} />
        <StatCard label="ID Cards" value={summary?.by_type?.ID_CARD ?? 0} />
        <StatCard label="Net Cash Flow" value={financial?.net_cash_flow ?? "0"} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h3 className="text-lg font-semibold">Documents by Type</h3>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            {Object.entries(summary?.by_type ?? {}).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                <span>{type}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
            {!summary || Object.keys(summary.by_type).length === 0 ? <p>No documents processed yet.</p> : null}
          </div>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h3 className="text-lg font-semibold">Recent Documents</h3>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            {summary?.recent_documents.map((doc) => (
              <div key={doc.id} className="rounded-xl bg-slate-50 px-4 py-3">
                <div className="flex items-center justify-between gap-4">
                  <span className="font-medium">{doc.document_type}</span>
                  <span className="text-xs uppercase text-emerald-600">{doc.status}</span>
                </div>
                <p className="mt-1 text-slate-500">{formatDate(doc.created_at)}</p>
              </div>
            ))}
            {!summary?.recent_documents.length ? <p>No recent documents available.</p> : null}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

