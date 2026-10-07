"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { setAuthToken } from "@/lib/auth";
import { api } from "@/lib/api";
import type { TokenResponse } from "@/types/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await api.post<TokenResponse>("/auth/register", { email, password });
      setAuthToken(response.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md rounded-2xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm uppercase tracking-[0.2em] text-brand-600">Secure OCR Platform</p>
        <h1 className="mt-3 text-3xl font-semibold">Register</h1>
        <p className="mt-2 text-sm text-slate-600">Create an account to manage extracted documents.</p>
        <div className="mt-6 space-y-4">
          <input
            className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-brand-500"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <input
            className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-brand-500"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            required
          />
        </div>
        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded-xl bg-brand-600 px-4 py-3 font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Create account"}
        </button>
        <p className="mt-4 text-sm text-slate-600">
          Already registered? <Link href="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}

