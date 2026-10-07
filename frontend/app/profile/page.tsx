"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { api } from "@/lib/api";
import type { User } from "@/types/api";

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api.get<User>("/auth/me").then(setUser).catch(() => undefined);
  }, []);

  return (
    <AppShell title="Profile" subtitle="Basic account information for the authenticated user.">
      <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <p className="text-sm text-slate-500">Email</p>
            <p className="mt-1 font-medium">{user?.email ?? "—"}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Active</p>
            <p className="mt-1 font-medium">{user?.is_active ? "Yes" : "No"}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">User ID</p>
            <p className="mt-1 break-all font-medium">{user?.id ?? "—"}</p>
          </div>
          <div>
            <p className="text-sm text-slate-500">Created At</p>
            <p className="mt-1 font-medium">{user?.created_at ?? "—"}</p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

