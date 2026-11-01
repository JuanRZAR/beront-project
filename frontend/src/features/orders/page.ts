import { api, jsonRequest } from "../../shared/http/client";
import { bindForm } from "../../shared/http/forms";
import { ApiError, errorMessage } from "../../shared/http/errors";
import { translate, money, type Locale } from "../../shared/i18n";
import {
  bindDialogs,
  byId,
  el,
  formatDate,
  openDialog,
} from "../../shared/components/dom";
import type { CheckoutOptions, PublicOrder } from "../../shared/http/contracts";

const locale: Locale = document.documentElement.lang === "en" ? "en" : "es";
const t = translate(locale);
const KEY = "beront.order";
const name = (row: { name_es: string; name_en: string }) =>
  locale === "en" ? row.name_en : row.name_es;
const safeWhatsApp = (value: string | null) => {
  if (!value) return null;
  try {
    const url = new URL(value);
    return url.origin === "https://wa.me" ? url.href : null;
  } catch {
    return null;
  }
};

function explanation(order: PublicOrder) {
  if (order.status.phase === "stock_issue") return t("explainStockIssue");
  if (order.payment_state === "pending")
    return order.payment_method === "whatsapp"
      ? t("explainWhatsApp")
      : t("explainTransfer");
  return t("explainUpdates");
}
function render(order: PublicOrder, received: boolean) {
  byId("order-result").hidden = false;
  byId("order-heading").textContent = received
    ? t("stepReceived")
    : t("orderFound");
  byId("order-code-value").textContent = order.code;
  byId("order-status").textContent = name(order.status);
  byId("order-explanation").textContent = explanation(order);
  byId("order-timeline").replaceChildren(
    ...order.history.map((event) => {
      const row = el("li");
      row.append(
        el("strong", name(event)),
        el("small", formatDate(event.created_at, locale)),
      );
      return row;
    }),
  );
  byId("order-guide").textContent = order.guide_number || t("afterShipment");
  byId("order-tracking").textContent =
    order.tracking_number || t("afterShipment");
  byId("order-lines").replaceChildren(
    ...order.items.map((line) => {
      const row = el("li");
      const text = el("div");
      text.append(
        el("strong", line.product_name),
        el("small", line.brand_name),
        el(
          "small",
          `${line.kind === "decant" ? "Decant" : t("fullBottle")} ${Number(line.volume_ml)} ml · ${line.quantity}`,
        ),
      );
      row.append(text, el("span", money(line.line_total)));
      return row;
    }),
  );
  byId("order-subtotal").textContent = money(order.subtotal);
  byId("order-shipping").textContent = money(order.shipping_fee);
  byId("order-total").textContent = money(order.total);
  const link = byId<HTMLAnchorElement>("order-whatsapp");
  const href = safeWhatsApp(order.whatsapp_url);
  link.hidden = !href;
  if (href) link.href = href;
  const failure = document.querySelector<HTMLElement>("[data-form-error]");
  if (failure) failure.hidden = true;
}
async function track(code: string, received: boolean) {
  const result = await api<PublicOrder>(
    "/api/v1/orders/track",
    jsonRequest("POST", { code }),
  );
  render(result.data, received);
}

const form = byId<HTMLFormElement>("tracking-form");
bindForm(
  form,
  async (values) => {
    byId("order-result").hidden = true;
    await track(String(values.get("code") ?? "").trim(), false);
  },
  locale,
);
const params = new URLSearchParams(location.search);
if (params.get("received") === "1") {
  byId("order-steps").hidden = false;
  let code = "";
  try {
    code = sessionStorage.getItem(KEY) ?? "";
  } catch {
    code = "";
  }
  if (code) {
    byId<HTMLInputElement>("tracking-code").value = code;
    track(code, true).catch((error) => {
      const failure = document.querySelector<HTMLElement>("[data-form-error]");
      if (failure) {
        failure.textContent = errorMessage(error, locale);
        failure.hidden = false;
      }
    });
  }
}

bindDialogs();
const dialog = byId<HTMLDialogElement>("recovery-dialog");
byId("open-recovery").addEventListener("click", async (event) => {
  openDialog(dialog, event.currentTarget as HTMLElement);
  const contact = byId<HTMLAnchorElement>("recovery-contact");
  if (!contact.hidden) return;
  try {
    const options = (await api<CheckoutOptions>("/api/v1/checkout/options"))
      .data;
    const number = options.settings?.whatsapp_number ?? "";
    if (/^[1-9][0-9]{7,14}$/.test(number)) {
      contact.href = "https://wa.me/" + number;
      contact.hidden = false;
    }
  } catch {
    contact.hidden = true;
  }
});
const recovery = byId<HTMLFormElement>("recovery-form");
bindForm(
  recovery,
  async (values) => {
    byId("recovery-status").textContent = "";
    try {
      await api(
        "/api/v1/orders/recovery",
        jsonRequest("POST", { cedula: String(values.get("cedula") ?? "") }),
      );
      byId("recovery-status").textContent = t("recoverySent");
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.body.code === "RECOVERY_COOLDOWN"
      ) {
        const seconds = Number(
          error.body.details.find((row) => row.field === "retry_after")
            ?.seconds ?? 600,
        );
        byId("recovery-status").textContent = t("recoveryCooldown").replace(
          "{minutes}",
          String(Math.max(1, Math.ceil(seconds / 60))),
        );
        return;
      }
      throw error;
    }
  },
  locale,
);
