import { defineMiddleware } from "astro:middleware";
import { isLocale } from "./shared/i18n";
import { serverGet } from "./shared/http/server";
import { ApiError } from "./shared/http/errors";
import type { Session } from "./shared/http/contracts";

export const onRequest = defineMiddleware(async (context, next) => {
  const trustedHost = ["localhost", "127.0.0.1", "[::1]"].includes(
    context.url.hostname,
  );
  let path = context.url.pathname;
  async function resolve(): Promise<Response> {
    if (!trustedHost) return new Response("Invalid host", { status: 400 });
    try {
      path = decodeURIComponent(path);
    } catch {
      return new Response("Invalid path", { status: 400 });
    }
    const first = path.split("/")[1];
    if (
      first &&
      !isLocale(first) &&
      ![
        "api",
        "media",
        "_astro",
        "@vite",
        "@id",
        "@fs",
        "src",
        "fonts",
        "brand",
        "temporal",
        "node_modules",
        "_image",
      ].some((prefix) => first.startsWith(prefix)) &&
      !path.includes(".")
    )
      return new Response("Not found", { status: 404 });
    context.locals.locale = isLocale(first) ? first : "es";
    context.locals.user = null;
    const locale = context.locals.locale;
    if (
      new RegExp("^/" + locale + "/admin(?:/|$)").test(path) &&
      !new RegExp("^/" + locale + "/admin/login/?$").test(path)
    ) {
      try {
        const result = await serverGet<Session>(
          "/api/v1/auth/session",
          context.request.headers.get("cookie") ?? "",
        );
        context.locals.user = result.data;
        const required = path.includes("/inventory")
          ? "inventory:read"
          : path.includes("/orders")
            ? "orders:read"
            : path.includes("/settings")
              ? "commerce:write"
              : path.includes("/media")
                ? "catalog:write"
                : path.includes("/products/new") ||
                    /\/products\/[a-f0-9-]+\/?$/.test(path)
                  ? "catalog:write"
                  : "catalog:read_private";
        if (
          result.data.role !== "admin" ||
          !result.data.permissions.includes(required)
        )
          return new Response("Forbidden", { status: 403 });
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          context.cookies.delete("beront_session", { path: "/" });
          return context.redirect("/" + locale + "/admin/login");
        }
        return context.rewrite(
          new URL("/" + locale + "/admin/login?unavailable=1", context.url),
        );
      }
    }
    return next();
  }
  const original = await resolve();
  const response = new Response(original.body, {
    status: original.status,
    statusText: original.statusText,
    headers: new Headers(original.headers),
  });
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  if (path.includes("/orders") || path.includes("/checkout"))
    response.headers.set("Referrer-Policy", "no-referrer");
  response.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=()",
  );
  if (!path.startsWith("/api/") && !path.startsWith("/media/"))
    response.headers.set(
      "Content-Security-Policy",
      "default-src 'self'; img-src 'self' data:; font-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'" +
        (trustedHost ? " ws://" + context.url.host : "") +
        "; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
    );
  if (
    path.includes("/admin") ||
    path.includes("/cart") ||
    path.includes("/checkout") ||
    path.includes("/orders") ||
    path.startsWith("/api/")
  )
    response.headers.set("Cache-Control", "no-store");
  return response;
});
