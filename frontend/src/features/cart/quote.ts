import type { Quote } from "../../shared/http/contracts";
import { ApiError } from "../../shared/http/errors";
const decimal = /^\d{1,10}\.\d{2}$/;
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
        item.quantity <= 20,
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
