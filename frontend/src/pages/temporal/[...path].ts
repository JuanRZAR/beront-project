import type { APIRoute } from "astro";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import {
  TemporaryError,
  temporaryCatalog,
  temporaryFacets,
  temporaryProduct,
  temporaryQuote,
  temporaryOverview,
} from "../../features/catalog/temporary";

export const ALL: APIRoute = async ({ request, params }) => {
  const json = (body: unknown, status = 200) =>
    Response.json(body, { status, headers: { "Cache-Control": "no-store" } });
  const error = (status: number, code: string) =>
    json(
      {
        error: {
          code,
          message: "",
          details: [],
          request_id: crypto.randomUUID(),
        },
      },
      status,
    );
  if (!import.meta.env.DEV) return error(404, "NOT_FOUND");
  const path = params.path ?? "";
  const assets: Record<string, [string, string]> = {
    "checkout.html": ["prototypes/checkout.html", "text/html; charset=utf-8"],
    "order-tracking.html": [
      "prototypes/order-tracking.html",
      "text/html; charset=utf-8",
    ],
    "admin-settings.html": [
      "prototypes/admin-settings.html",
      "text/html; charset=utf-8",
    ],
    "admin-media.html": [
      "prototypes/admin-media.html",
      "text/html; charset=utf-8",
    ],
    "admin-orders.html": [
      "prototypes/admin-orders.html",
      "text/html; charset=utf-8",
    ],
    "checkout.css": ["assets/checkout.css", "text/css; charset=utf-8"],
    "checkout.js": ["assets/checkout.js", "text/javascript; charset=utf-8"],
    "admin-commerce.css": [
      "assets/admin-commerce.css",
      "text/css; charset=utf-8",
    ],
    "admin-commerce.js": [
      "assets/admin-commerce.js",
      "text/javascript; charset=utf-8",
    ],
    "seed/catalog.json": [
      "../backend/semillas/catalogo/catalogo.json",
      "application/json; charset=utf-8",
    ],
    "": ["prototypes/catalog-refined.html", "text/html; charset=utf-8"],
    "catalog-refined.html": [
      "prototypes/catalog-refined.html",
      "text/html; charset=utf-8",
    ],
    "catalog-refined.css": [
      "assets/catalog-refined.css",
      "text/css; charset=utf-8",
    ],
    "catalog-refined.js": [
      "assets/catalog-refined.js",
      "text/javascript; charset=utf-8",
    ],
    "catalog-import.html": [
      "prototypes/catalog-import.html",
      "text/html; charset=utf-8",
    ],
    "tokens.css": ["tokens.css", "text/css; charset=utf-8"],
    "catalog-import.css": [
      "assets/catalog-import.css",
      "text/css; charset=utf-8",
    ],
    "catalog-import.js": [
      "assets/catalog-import.js",
      "text/javascript; charset=utf-8",
    ],
    "assets/cormorant-garamond.ttf": [
      "assets/cormorant-garamond.ttf",
      "font/ttf",
    ],
    "assets/source-sans-3.ttf": ["assets/source-sans-3.ttf", "font/ttf"],
  };
  const seedImage = /^seed\/media\/([a-f0-9]{32}\.webp)$/.exec(path);
  if (seedImage?.[1])
    assets[path] = [
      "../backend/semillas/catalogo/imagenes/" + seedImage[1],
      "image/webp",
    ];
  try {
    if (assets[path]) {
      if (!["GET", "HEAD"].includes(request.method))
        return error(405, "METHOD_NOT_ALLOWED");
      const [file, mime] = assets[path];
      const contents = await readFile(
        resolve(process.cwd(), "../design", file),
      );
      return new Response(request.method === "HEAD" ? null : contents, {
        headers: { "Content-Type": mime, "Cache-Control": "no-store" },
      });
    }
    if (path === "api/v1/cart/quote" && request.method === "POST") {
      if (!request.headers.get("content-type")?.startsWith("application/json"))
        return error(415, "UNSUPPORTED_MEDIA_TYPE");
      if (Number(request.headers.get("content-length")) > 65536)
        return error(413, "PAYLOAD_TOO_LARGE");
      const reader = request.body?.getReader();
      const chunks: Uint8Array[] = [];
      let size = 0;
      if (reader) {
        try {
          for (;;) {
            const { value, done } = await reader.read();
            if (done) break;
            size += value.length;
            if (size > 65536) {
              await reader.cancel();
              return error(413, "PAYLOAD_TOO_LARGE");
            }
            chunks.push(value);
          }
        } catch {
          return error(400, "BAD_REQUEST");
        } finally {
          reader.releaseLock();
        }
      }
      const bytes = new Uint8Array(size);
      let offset = 0;
      for (const chunk of chunks) {
        bytes.set(chunk, offset);
        offset += chunk.length;
      }
      let body: unknown;
      try {
        body = JSON.parse(new TextDecoder().decode(bytes));
      } catch {
        return error(400, "BAD_REQUEST");
      }
      return json(temporaryQuote(body));
    }
    if (request.method !== "GET") return error(405, "METHOD_NOT_ALLOWED");
    if (path === "api/v1/catalog/products")
      return json(temporaryCatalog(new URL(request.url).searchParams));
    if (path === "api/v1/catalog/facets")
      return json({ data: temporaryFacets() });
    if (path === "api/v1/catalog/overview")
      return json({ data: temporaryOverview() });
    const detail = /^api\/v1\/catalog\/products\/([a-f0-9-]{36})$/.exec(path);
    if (detail?.[1]) return json({ data: temporaryProduct(detail[1]) });
    return error(404, "NOT_FOUND");
  } catch (err) {
    if (err instanceof TemporaryError) return error(err.status, err.code);
    return error(503, "PREVIEW_UNAVAILABLE");
  }
};
