import type { DocumentType } from "@/types/api";
import { getAuthToken } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers ?? {});
  const token = typeof window !== "undefined" ? getAuthToken() : null;
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    const fallback = { error: { message: "Request failed." } };
    const body = (await response.json().catch(() => fallback)) as { error?: { message?: string } };
    throw new Error(body.error?.message ?? "Request failed.");
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  delete: <T>(path: string) =>
    request<T>(path, {
      method: "DELETE",
    }),
  upload: <T>(path: string, file: File, documentType?: DocumentType) => {
    const formData = new FormData();
    formData.append("file", file);
    if (documentType) {
      formData.append("document_type", documentType);
    }
    return request<T>(path, {
      method: "POST",
      body: formData,
    });
  },
};

