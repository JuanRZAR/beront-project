import { api, jsonRequest } from "../../shared/http/client";
import { bindForm } from "../../shared/http/forms";
import { ApiError, errorMessage } from "../../shared/http/errors";
import { translate, money, type Locale } from "../../shared/i18n";
import { bindDialogs, byId, el, openDialog } from "../../shared/components/dom";
import { cart } from "../cart/store";
import { validateQuote } from "../cart/quote";
import type {
  Bank,
  CheckoutOptions,
  CheckoutQuote,
  QuoteLine,
} from "../../shared/http/contracts";

const locale: Locale = document.documentElement.lang === "en" ? "en" : "es";
const t = translate(locale);
const form = byId<HTMLFormElement>("purchase-form");
const status = byId("purchase-status");
const items = cart.read();
let options: CheckoutOptions;
let quote: CheckoutQuote | null = null;
let selectedBank: string | null = null;
let operation: { signature: string; id: string } | null = null;

function renderLines(lines: QuoteLine[]) {
  byId("checkout-lines").replaceChildren(
    ...lines.map((line) => {
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
}
function renderBanks(banks: Bank[]) {
  const buttons = byId("bank-options");
  if (!banks.some((bank) => bank.id === selectedBank))
    selectedBank = banks[0]?.id ?? null;
  buttons.replaceChildren(
    ...banks.map((bank) => {
      const button = el("button", bank.bank_name, {
        type: "button",
        "aria-pressed": String(bank.id === selectedBank),
      });
      button.addEventListener("click", () => {
        selectedBank = bank.id;
        renderBanks(banks);
      });
      return button;
    }),
  );
  const selected = banks.find((bank) => bank.id === selectedBank);
  byId("bank-details").replaceChildren(
    ...(selected
      ? [
          el("strong", selected.bank_name),
          el("p", `${selected.account_type} · ${selected.account_number}`),
          el("p", selected.holder_name),
          el("p", selected.holder_identification),
        ]
      : [el("p", t("noBanks"))]),
  );
}
function termsText() {
  return (
    quote?.terms_text ??
    options.settings?.[locale === "en" ? "terms_en" : "terms_es"] ??
    ""
  );
}
function currentBanks() {
  return quote?.banks?.length ? quote.banks : options.banks;
}
function paymentMode() {
  return (
    form.querySelector<HTMLInputElement>("input[name=payment]:checked")
      ?.value ?? "whatsapp"
  );
}
function updatePayment() {
  const bank = paymentMode() === "bank_transfer";
  byId("bank-panel").hidden = !bank;
  byId("whatsapp-panel").hidden = bank;
  const receipt = byId<HTMLInputElement>("receipt");
  receipt.required = bank;
  receipt.disabled = !bank;
  if (bank) renderBanks(currentBanks());
}
function renderTotals() {
  byId("checkout-shipping").textContent = quote
    ? money(quote.shipping_fee)
    : t("byCity");
  byId("checkout-total").textContent = quote
    ? money(quote.total)
    : t("totalPending");
}
async function requote() {
  const city = byId<HTMLSelectElement>("city").value;
  if (!city) {
    quote = null;
    renderTotals();
    return;
  }
  try {
    const result = await api<CheckoutQuote>(
      "/api/v1/checkout/quote",
      jsonRequest("POST", { locale, items, city_id: city }),
    );
    quote = result.data;
    renderLines(quote.items);
    byId("checkout-subtotal").textContent = money(quote.subtotal);
    renderTotals();
    status.textContent = "";
    if (paymentMode() === "bank_transfer") renderBanks(currentBanks());
  } catch (error) {
    quote = null;
    renderTotals();
    status.textContent = errorMessage(error, locale);
  }
}
function fillCities() {
  const province = byId<HTMLSelectElement>("province").value;
  const city = byId<HTMLSelectElement>("city");
  city.replaceChildren(
    el("option", t("select"), { value: "" }),
    ...options.cities
      .filter((row) => row.province_id === province)
      .map((row) => el("option", row.name, { value: row.id })),
  );
  city.disabled = !province;
  quote = null;
  renderTotals();
}
function showUnavailable(message?: string) {
  const notice = byId("checkout-unavailable");
  if (message) notice.textContent = message;
  notice.hidden = false;
}

async function start() {
  if (!items.length) {
    byId("checkout-empty").hidden = false;
    return;
  }
  try {
    options = (await api<CheckoutOptions>("/api/v1/checkout/options")).data;
  } catch (error) {
    showUnavailable(errorMessage(error, locale));
    return;
  }
  if (!/^[1-9][0-9]{7,14}$/.test(options.settings?.whatsapp_number ?? "")) {
    const whatsapp = form.querySelector<HTMLInputElement>(
      "input[value=whatsapp]",
    )!;
    whatsapp.disabled = true;
    whatsapp.checked = false;
    form.querySelector<HTMLInputElement>(
      "input[value=bank_transfer]",
    )!.checked = true;
    byId("whatsapp-off").hidden = false;
  }
  const provinces = options.provinces.filter((province) =>
    options.cities.some((city) => city.province_id === province.id),
  );
  if (!options.settings || !provinces.length || !options.banks.length) {
    showUnavailable();
    return;
  }
  let preview;
  try {
    preview = validateQuote(
      (
        await api<ReturnType<typeof validateQuote>>(
          "/api/v1/cart/quote",
          jsonRequest("POST", { locale, items }),
        )
      ).data,
    );
  } catch (error) {
    showUnavailable(errorMessage(error, locale));
    return;
  }
  renderLines(preview.items);
  byId("checkout-subtotal").textContent = money(preview.total);
  const province = byId<HTMLSelectElement>("province");
  province.replaceChildren(
    el("option", t("select"), { value: "" }),
    ...provinces.map((row) => el("option", row.name, { value: row.id })),
  );
  fillCities();
  form.hidden = false;
  updatePayment();
}

form
  .querySelectorAll<HTMLInputElement>("input[name=payment]")
  .forEach((input) => input.addEventListener("change", updatePayment));
byId("province").addEventListener("change", fillCities);
byId("city").addEventListener("change", requote);
byId<HTMLInputElement>("accept-terms").addEventListener("change", (event) => {
  byId<HTMLButtonElement>("pay-button").disabled = !(
    event.target as HTMLInputElement
  ).checked;
});
byId("open-terms").addEventListener("click", (event) => {
  byId("terms-text").textContent = termsText();
  openDialog(
    byId<HTMLDialogElement>("terms-dialog"),
    event.currentTarget as HTMLElement,
  );
});
bindDialogs();

bindForm(
  form,
  async (values) => {
    if (!quote) throw new Error("NO_QUOTE");
    const bank = paymentMode() === "bank_transfer";
    const file = byId<HTMLInputElement>("receipt").files?.[0];
    const text = (key: string) => String(values.get(key) ?? "").trim();
    const payload = {
      locale,
      items,
      city_id: quote.city_id,
      quote_token: quote.quote_token,
      customer: {
        cedula: text("cedula"),
        first_name: text("first_name"),
        last_name: text("last_name"),
        phone: text("phone"),
        email: text("email"),
      },
      address: text("address"),
      payment_method: bank ? "bank_transfer" : "whatsapp",
      ...(bank ? { bank_id: selectedBank } : {}),
      terms_accepted: true,
    };
    const signature = JSON.stringify([payload, file?.name, file?.size]);
    if (operation?.signature !== signature)
      operation = { signature, id: crypto.randomUUID() };
    const body = { ...payload, operation_id: operation.id };
    let request: RequestInit;
    if (bank) {
      if (!file)
        throw new ApiError(422, {
          code: "RECEIPT_REQUIRED",
          message: "",
          details: [],
        });
      const data = new FormData();
      data.set("payload", JSON.stringify(body));
      data.set("file", file);
      request = { method: "POST", body: data };
    } else request = jsonRequest("POST", body);
    status.textContent = t("sendingOrder");
    try {
      const result = await api<{ code: string }>("/api/v1/orders", request);
      try {
        sessionStorage.setItem("beront.order", result.data.code);
      } catch {
        // The code remains visible on the next page only when storage is available.
      }
      for (const item of cart.read()) cart.remove(item.variant_id);
      location.assign("/" + locale + "/orders?received=1");
    } catch (error) {
      status.textContent = "";
      if (
        error instanceof ApiError &&
        ["QUOTE_CHANGED", "INSUFFICIENT_STOCK", "BANK_UNAVAILABLE"].includes(
          error.body.code,
        )
      ) {
        operation = null;
        await requote();
      }
      throw error;
    }
  },
  locale,
);
void start();
