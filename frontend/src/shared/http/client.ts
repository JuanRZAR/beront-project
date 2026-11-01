import type { Envelope } from "./contracts";
import { ApiError } from "./errors";

export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<Envelope<T>> {
  if (!path.startsWith("/api/v1/")) throw new Error("Invalid API path.");
  const method = (options.method ?? "GET").toUpperCase();
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (
    !["GET", "HEAD", "OPTIONS"].includes(method) &&
    path !== "/api/v1/cart/quote"
  ) {
    const token = await api<{ csrf_token: string }>("/api/v1/auth/csrf");
    headers.set("X-CSRFToken", token.data.csrf_token);
  }
  if (options.body && !(options.body instanceof FormData))
    headers.set("Content-Type", "application/json");
  let response: Response;
  try {
    response = await fetch(path, {
      ...options,
      method,
      headers,
      credentials: "same-origin",
      cache: "no-store",
      signal: options.signal ?? AbortSignal.timeout(12000),
    });
  } catch {
    throw new ApiError(503, {
      code: "SERVICE_UNAVAILABLE",
      message: "",
      details: [],
    });
  }
  if (response.status === 204) return { data: null as T };
  let result;
  try {
    result = await response.json();
  } catch {
    throw new ApiError(503, {
      code: "SERVICE_UNAVAILABLE",
      message: "",
      details: [],
    });
  }
  if (!response.ok) {
    if (response.status === 401 && path.startsWith("/api/v1/admin/")) {
      const locale = document.documentElement.lang === "en" ? "en" : "es";
      location.assign("/" + locale + "/admin/login");
    }
    throw new ApiError(
      response.status,
      result.error ?? { code: "SERVICE_UNAVAILABLE", message: "", details: [] },
    );
  }
  return result as Envelope<T>;
}
export function jsonRequest(method: string, data: unknown): RequestInit {
  return { method, body: JSON.stringify(data) };
}
