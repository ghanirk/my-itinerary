import { getToken } from "../lib/authStorage";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  auth?: boolean; // sertakan Authorization header (default: true)
}

/**
 * Wrapper fetch tipis untuk memanggil backend FastAPI.
 * Menyisipkan token JWT (kalau ada) dan melempar ApiError dengan pesan
 * `detail` dari FastAPI supaya gampang ditampilkan ke user.
 */
export async function apiFetch<T>(
  path: string,
  { method = "GET", body, auth = true }: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      (data && typeof data.detail === "string" && data.detail) ||
      "Terjadi kesalahan, coba lagi.";
    throw new ApiError(detail, response.status);
  }

  return data as T;
}
