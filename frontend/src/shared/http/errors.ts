import type { ApiErrorBody } from "./contracts";
import type { Locale } from "../i18n";
import { translate } from "../i18n";

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: ApiErrorBody,
  ) {
    super(body.code);
  }
}
export function errorMessage(error: unknown, locale: Locale) {
  const t = translate(locale);
  if (!(error instanceof ApiError)) return t("requestFailed");
  const key: Record<string, string> = {
    UNAUTHORIZED: "sessionExpired",
    CSRF_INVALID: "csrf",
    VERSION_CONFLICT: "conflict",
    DATA_CONFLICT: "conflict",
    OPERATION_CONFLICT: "conflict",
    INSUFFICIENT_STOCK: "availableChanged",
    VALIDATION_ERROR: "validation",
    INVALID_IMAGE: "badImage",
    INVALID_IMAGE_TYPE: "badImage",
    IMAGE_TOO_LARGE: "tooLarge",
    PAYLOAD_TOO_LARGE: "tooLarge",
    RATE_LIMITED: "retryLimit",
    NEGATIVE_STOCK: "invalidAdjustment",
    INVALID_ADJUSTMENT: "invalidAdjustment",
    IMAGE_LIMIT: "imageLimits",
    PRODUCT_NOT_READY: "created",
    SERVICE_UNAVAILABLE: "loadError",
    SCHEMA_ERROR: "schemaError",
    QUOTE_CHANGED: "quoteChanged",
    UNAVAILABLE_PRODUCT: "availableChanged",
    BANK_UNAVAILABLE: "quoteChanged",
    CHECKOUT_NOT_CONFIGURED: "checkoutNotConfigured",
    RECEIPT_REQUIRED: "receiptRequired",
    RECOVERY_COOLDOWN: "recoveryCooldown",
    RECOVERY_UNAVAILABLE: "recoveryUnavailable",
    PAYMENT_REQUIRED: "paymentRequired",
    TRACKING_REQUIRED: "trackingRequired",
    INVALID_TRANSITION: "invalidTransition",
    ORDER_CANCELLED: "invalidTransition",
    INVALID_OPTION: "invalidOption",
    ASSET_IN_USE: "assetInUse",
    INVALID_ASSET: "badImage",
    DEFINITION_IN_USE: "definitionInUse",
    NOT_FOUND: "notFound",
    WHATSAPP_NOT_CONFIGURED: "whatsappNotConfigured",
    INVALID_PHONE: "invalidPhone",
  };
  return t(key[error.body.code] ?? "requestFailed");
}
export function showError(
  element: HTMLElement,
  error: unknown,
  locale: Locale,
) {
  element.textContent = errorMessage(error, locale);
  element.hidden = false;
  element.setAttribute("role", "alert");
  element.focus();
}
