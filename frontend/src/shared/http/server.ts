import { AsyncLocalStorage } from "node:async_hooks";
import { ApiError } from "./errors";
import type { Envelope } from "./contracts";

export const ADDRESS = /^[0-9a-fA-F:.]{2,45}$/;
export const LOCAL_HOSTS = ["localhost", "127.0.0.1", "[::1]"];
const requestAddress = new AsyncLocalStorage<string>();

export function clientIp(request: Request, connection: string) {
  const forwarded = request.headers.get("x-real-ip")?.trim() ?? "";
  if (process.env.TRUST_PROXY === "true" && ADDRESS.test(forwarded))
    return forwarded;
  return ADDRESS.test(connection) ? connection : "";
}
export function withClientIp<T>(address: string, run: () => T): T {
  return requestAddress.run(address, run);
}
function forwardedAddress(): Record<string, string> {
  const address = requestAddress.getStore();
  return address ? { "X-Real-IP": address } : {};
}

export function backendUrl() {
  const target = new URL(
    process.env.BACKEND_URL ??
      import.meta.env.BACKEND_URL ??
      "http://127.0.0.1:5000",
  );
  if (
    target.protocol !== "http:" ||
    ![...LOCAL_HOSTS, "api"].includes(target.hostname) ||
    target.username ||
    target.password ||
    target.pathname !== "/" ||
    target.search ||
    target.hash
  )
    throw new Error("BACKEND_URL must be an internal HTTP origin.");
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
        ...forwardedAddress(),
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
