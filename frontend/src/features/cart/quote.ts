import type { Quote } from "../../shared/http/contracts";
import { api, jsonRequest } from "../../shared/http/client";
import { ApiError } from "../../shared/http/errors";
import type { Locale } from "../../shared/i18n";
import { cart } from "./store";
const decimal = /^\d{1,10}\.\d{2}$/;
const uuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
const photo = /^\/media\/[a-f0-9]{32}\.webp$/;
function validOption(option: unknown) {
  if (!option || typeof option !== "object") return false;
  const { variant_id, volume_ml, unit_price } = option as Record<
    string,
    unknown
  >;
  return (
    typeof variant_id === "string" &&
    uuid.test(variant_id) &&
    typeof volume_ml === "string" &&
    decimal.test(volume_ml) &&
    typeof unit_price === "string" &&
    decimal.test(unit_price)
  );
}
export function validateQuote(value: Quote): Quote {
  if (
    value.currency !== "USD" ||
    !decimal.test(value.total) ||
    !Array.isArray(value.items) ||
    !value.items.every(
      (item) =>
        typeof item.variant_id === "string" &&
        typeof item.product_name === "string" &&
        typeof item.brand_name === "string" &&
        ["decant", "full_bottle"].includes(item.kind) &&
        decimal.test(item.unit_price) &&
        decimal.test(item.line_total) &&
        decimal.test(item.volume_ml) &&
        Number.isInteger(item.quantity) &&
        item.quantity > 0 &&
        item.quantity <= 20 &&
        (item.image_url === undefined ||
          item.image_url === null ||
          photo.test(item.image_url)) &&
        (item.options === undefined ||
          (Array.isArray(item.options) && item.options.every(validOption))),
    )
  )
    throw new ApiError(502, { code: "SCHEMA_ERROR", message: "", details: [] });
  if (value.whatsapp_url !== null) {
    let url: URL;
    try {
      url = new URL(value.whatsapp_url);
    } catch {
      throw new ApiError(502, {
        code: "SCHEMA_ERROR",
        message: "",
        details: [],
      });
    }
    if (
      url.origin !== "https://wa.me" ||
      url.username ||
      url.password ||
      !/^\/[1-9]\d{7,14}$/.test(url.pathname) ||
      !url.searchParams.has("text")
    )
      throw new ApiError(502, {
        code: "SCHEMA_ERROR",
        message: "",
        details: [],
      });
  }
  return value;
}
export function quoteFingerprint(quote: Quote) {
  return JSON.stringify([
    quote.total,
    ...quote.items.map((item) => [
      item.variant_id,
      item.quantity,
      item.unit_price,
      item.line_total,
    ]),
  ]);
}
const pending = new Map<string, Promise<Quote>>();
export function requestQuote(locale: Locale) {
  const body = { locale, items: cart.read() },
    key = JSON.stringify(body),
    existing = pending.get(key);
  if (existing) return existing;
  const request = api<Quote>("/api/v1/cart/quote", jsonRequest("POST", body))
    .then((result) => validateQuote(result.data))
    .finally(() => pending.delete(key));
  pending.set(key, request);
  return request;
}
