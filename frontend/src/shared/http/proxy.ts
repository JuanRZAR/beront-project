import { backendUrl } from "./server";

function failure(status: number, code: string) {
  return Response.json(
    {
      error: {
        code,
        message: "",
        details: [],
        request_id: crypto.randomUUID(),
      },
    },
    { status, headers: { "Cache-Control": "no-store" } },
  );
}
const ADDRESS = /^[0-9a-fA-F:.]{2,45}$/;
export async function proxy(
  request: Request,
  path: string,
  media = false,
  clientAddress = "",
): Promise<Response> {
  if (
    media
      ? !/^[a-f0-9]{32}\.webp$/.test(path)
      : !/^v1\/(catalog|admin|auth|cart|checkout|orders)(\/|$)/.test(path)
  )
    return failure(404, "NOT_FOUND");
  if (
    path.includes("\\") ||
    path.split("/").some((part) => {
      try {
        return [".", ".."].includes(decodeURIComponent(part));
      } catch {
        return true;
      }
    })
  )
    return failure(404, "NOT_FOUND");
  if (media && !["GET", "HEAD"].includes(request.method))
    return failure(405, "METHOD_NOT_ALLOWED");
  const target = new URL(backendUrl());
  target.pathname = (media ? "/media/" : "/api/") + path;
  target.search = new URL(request.url).search;
  const headers = new Headers();
  for (const key of [
    "accept",
    "content-type",
    "cookie",
    "origin",
    "x-csrftoken",
    "if-none-match",
    "if-modified-since",
  ]) {
    const value = request.headers.get(key);
    if (value) headers.set(key, value);
  }
  if (ADDRESS.test(clientAddress)) headers.set("x-client-ip", clientAddress);
  let body: Uint8Array<ArrayBuffer> | undefined;
  if (!["GET", "HEAD"].includes(request.method)) {
    const maximum =
      request.method === "POST" &&
      request.headers.get("content-type")?.startsWith("multipart/form-data") &&
      (path.endsWith("/images") ||
        path.endsWith("/receipts") ||
        path === "v1/orders" ||
        path === "v1/admin/media")
        ? 5 * 1024 * 1024 + 65536
        : 65536;
    if (Number(request.headers.get("content-length")) > maximum)
      return failure(413, "PAYLOAD_TOO_LARGE");
    const reader = request.body?.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    if (reader) {
      try {
        for (;;) {
          const chunk = await reader.read();
          if (chunk.done) break;
          size += chunk.value.length;
          if (size > maximum) {
            await reader.cancel();
            return failure(413, "PAYLOAD_TOO_LARGE");
          }
          chunks.push(chunk.value);
        }
      } catch {
        return failure(400, "BAD_REQUEST");
      } finally {
        reader.releaseLock();
      }
    }
    body = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) {
      body.set(chunk, offset);
      offset += chunk.length;
    }
  }
  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method: request.method,
      headers,
      body,
      redirect: "manual",
      signal: AbortSignal.timeout(10000),
    });
  } catch {
    return failure(503, "SERVICE_UNAVAILABLE");
  }
  const outgoing = new Headers();
  for (const key of [
    "content-type",
    "cache-control",
    "etag",
    "last-modified",
    "x-request-id",
    "retry-after",
    "allow",
    "content-disposition",
  ]) {
    const value = upstream.headers.get(key);
    if (value) outgoing.set(key, value);
  }
  for (const cookie of upstream.headers.getSetCookie())
    outgoing.append("Set-Cookie", cookie);
  if (!media) outgoing.set("Cache-Control", "no-store");
  return new Response(upstream.body, {
    status: upstream.status,
    headers: outgoing,
  });
}
