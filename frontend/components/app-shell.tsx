"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { PropsWithChildren, useEffect, useState } from "react";

import { clearAuthToken } from "@/lib/auth";
import { api } from "@/lib/api";
import type { User } from "@/types/api";

type Props = PropsWithChildren<{ title: string; subtitle?: string }>;

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/upload", label: "Upload" },
  { href: "/documents", label: "Documents" },
  { href: "/profile", label: "Profile" },
];

export function AppShell({ title, subtitle, children }: Props) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<User>("/auth/me")
      .then(setUser)
      .catch(() => {
        clearAuthToken();
        router.push("/login");
      })
      .finally(() => setLoading(false));
  }, [router]);

  const logout = async () => {
    try {
      await api.post<{ message: string }>("/auth/logout", {});
    } catch {
      // best effort
    }
    clearAuthToken();
    router.push("/login");
  };

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-slate-600">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <aside className="hidden w-64 shrink-0 rounded-2xl bg-slate-900 p-6 text-white lg:block">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Secure OCR Platform</p>
            <h1 className="mt-2 text-2xl font-semibold">Document Vault</h1>
          </div>
          <nav className="mt-8 space-y-2">
            {navItems.map((item) => {
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`block rounded-xl px-4 py-3 text-sm transition ${
                    active ? "bg-brand-600 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="mt-10 rounded-xl border border-slate-700 p-4">
            <p className="text-sm font-medium">Signed in as</p>
            <p className="mt-2 break-all text-sm text-slate-300">{user?.email}</p>
            <button
              type="button"
              onClick={logout}
              className="mt-4 w-full rounded-lg border border-slate-600 px-3 py-2 text-sm hover:bg-slate-800"
            >
              Logout
            </button>
          </div>
        </aside>
        <main className="flex-1">
          <header className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <p className="text-sm text-slate-500">Sensitive data is access-controlled and masked where appropriate.</p>
            <h2 className="mt-2 text-3xl font-semibold">{title}</h2>
            {subtitle ? <p className="mt-2 text-slate-600">{subtitle}</p> : null}
          </header>
          <section className="mt-6">{children}</section>
        </main>
      </div>
    </div>
  );
}

