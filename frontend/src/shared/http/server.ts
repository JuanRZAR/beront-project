import { ApiError } from "./errors";
import type { Envelope } from "./contracts";

export function backendUrl() {
  const target = new URL(
    import.meta.env.BACKEND_URL ??
      process.env.BACKEND_URL ??
      "http://127.0.0.1:5000",
  );
  if (
    target.protocol !== "http:" ||
    !["localhost", "127.0.0.1", "[::1]"].includes(target.hostname) ||
    target.username ||
    target.password ||
    target.pathname !== "/" ||
    target.search ||
    target.hash
  )
    throw new Error("BACKEND_URL must be a local HTTP origin.");
  return target.origin;
}
export async function serverGet<T>(
  path: string,
  cookie = "",
): Promise<Envelope<T>> {
  if (!path.startsWith("/api/v1/"))
    throw new Error("Invalid internal API path.");
  let response: Response;
  try {
    response = await fetch(new URL(path, backendUrl()), {
      headers: {
        Accept: "application/json",
        ...(cookie ? { Cookie: cookie } : {}),
      },
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.timeout(8000),
    });
  } catch {
    throw new ApiError(503, {
      code: "SERVICE_UNAVAILABLE",
      message: "",
      details: [],
    });
  }
  let body;
  try {
    body = await response.json();
  } catch {
    throw new ApiError(503, {
      code: "SERVICE_UNAVAILABLE",
      message: "",
      details: [],
    });
  }
  if (!response.ok)
    throw new ApiError(
      response.status,
      body.error ?? { code: "SERVICE_UNAVAILABLE", message: "", details: [] },
    );
  return body as Envelope<T>;
}
