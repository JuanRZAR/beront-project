import { api, jsonRequest } from "../../shared/http/client";
import { ApiError, showError } from "../../shared/http/errors";
import type { Quote, QuoteLine } from "../../shared/http/contracts";
import { translate, money, number, type Locale } from "../../shared/i18n";
import { createStepper } from "../../shared/components/stepper";
import { toast } from "../../shared/components/toast";
import { bindDialogs, byId, el } from "../../shared/components/dom";
import { cart } from "./store";
import { validateQuote, quoteFingerprint } from "./quote";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const dialog = byId<HTMLDialogElement>("cart-dialog"),
  status = byId("cart-status"),
  notice = byId("cart-notice"),
  items = byId("cart-items"),
  summary = byId("cart-summary"),
  whatsapp = byId<HTMLButtonElement>("continue-whatsapp"),
  floating = byId("floating-cart");
let current: Quote | null = null,
  epoch = 0,
  busy = false,
  origin: HTMLElement | null = null;
const remembered = new Map<string, QuoteLine>();
function unavailableIds(error: unknown) {
  return new Set(
    error instanceof ApiError
      ? error.body.details
          .map((detail) => detail.variant_id)
          .filter((value): value is string => !!value)
      : [],
  );
}
function focusKey(): [string, string] | null {
  const active = document.activeElement as HTMLElement | null,
    row = active?.closest<HTMLElement>("[data-variant]");
  if (!row?.dataset.variant || !active) return null;
  return [
    row.dataset.variant,
    active.dataset.step ?? (active.matches("input") ? "input" : "remove"),
  ];
}
function restoreFocus(key: [string, string] | null) {
  if (!key) return;
  const row = items.querySelector<HTMLElement>(
    `[data-variant="${CSS.escape(key[0])}"]`,
  );
  const target = row?.querySelector<HTMLButtonElement>(
    key[1] === "input"
      ? "input"
      : key[1] === "remove"
        ? ".remove-item"
        : `[data-step="${key[1]}"]`,
  );
  if (target && !target.disabled) target.focus();
  else (row?.querySelector("input") ?? byId("cart-title")).focus();
}
function syncFloating() {
  floating.hidden = dialog.open || cart.read().length === 0;
}
function render(quote: Quote | null, unavailable = new Set<string>()) {
  const key = focusKey();
  const lines = cart.read();
  items.replaceChildren(
    ...lines.map((item) => {
      const line =
        quote?.items.find((entry) => entry.variant_id === item.variant_id) ??
        remembered.get(item.variant_id);
      const row = el("div", undefined, { class: "cart-row" });
      row.dataset.variant = item.variant_id;
      const text = el("div");
      const name = line ? line.product_name : t("productUnavailable");
      text.append(
        el("strong", name),
        el(
          "p",
          line
            ? line.brand_name +
                " · " +
                t(line.kind === "decant" ? "decant" : "fullBottle") +
                " · " +
                number(line.volume_ml) +
                " ml"
            : "",
          { class: "hint" },
        ),
      );
      if (unavailable.has(item.variant_id))
        text.append(el("p", t("lineUnavailable"), { class: "danger-text" }));
      const remove = el("button", t("remove"), {
        type: "button",
        class: "text-button remove-item",
        "aria-label": t("remove") + ": " + name,
      });
      remove.addEventListener("click", () => {
        cart.remove(item.variant_id);
        render(quote, unavailable);
        void load();
      });
      row.append(
        text,
        el("strong", quote && line ? money(line.line_total) : "—", {
          class: "cart-row-total",
        }),
        createStepper(
          locale,
          name,
          item.quantity,
          (value) => {
            cart.quantity(item.variant_id, value);
            void load();
          },
          () => toast(t("limit")),
        ),
        remove,
      );
      return row;
    }),
  );
  byId("cart-total").textContent = quote ? money(quote.total) : "—";
  summary.hidden = !quote || !lines.length;
  whatsapp.disabled = !quote?.whatsapp_url;
  byId("whatsapp-unavailable").hidden = !quote || !!quote.whatsapp_url;
  restoreFocus(key);
}
async function quoteCart() {
  return validateQuote(
    (
      await api<Quote>(
        "/api/v1/cart/quote",
        jsonRequest("POST", { locale, items: cart.read() }),
      )
    ).data,
  );
}
async function load() {
  const request = ++epoch;
  current = null;
  notice.hidden = true;
  whatsapp.disabled = true;
  if (!cart.read().length) {
    status.textContent = t("emptyCart");
    render(null);
    return;
  }
  status.textContent = t("checking");
  try {
    const quote = await quoteCart();
    if (request !== epoch) return;
    current = quote;
    quote.items.forEach((line) => remembered.set(line.variant_id, line));
    status.textContent = "";
    render(quote);
    if (!cart.persistent) {
      notice.textContent = t("storageUnavailable");
      notice.hidden = false;
    }
  } catch (error) {
    if (request !== epoch) return;
    status.textContent = "";
    render(null, unavailableIds(error));
    showError(notice, error, locale);
  }
}
function open(opener: HTMLElement | null) {
  origin = opener;
  if (!dialog.open) dialog.showModal();
  syncFloating();
  render(null);
  void load();
}
document.addEventListener("click", (event) => {
  const link = (event.target as HTMLElement).closest<HTMLElement>(
    "[data-open-cart]",
  );
  const mouse = event as MouseEvent;
  if (!link || mouse.button !== 0 || mouse.ctrlKey || mouse.metaKey) return;
  event.preventDefault();
  open(link);
});
window.addEventListener("beront:open-cart", (event) =>
  open((event as CustomEvent<HTMLElement | null>).detail),
);
dialog.addEventListener("close", () => {
  syncFloating();
  if (origin?.isConnected) origin.focus({ preventScroll: true });
});
window.addEventListener("beront:cart", syncFloating);
window.addEventListener("storage", () => {
  cart.invalidate();
  syncFloating();
  if (dialog.open) void load();
});
byId("clear-cart").addEventListener("click", () => {
  for (const item of cart.read()) cart.remove(item.variant_id);
  void load();
});
whatsapp.addEventListener("click", async () => {
  if (!current || busy) return;
  const previous = quoteFingerprint(current),
    request = ++epoch,
    label = whatsapp.querySelector("span")!;
  busy = true;
  items.inert = true;
  whatsapp.disabled = true;
  label.textContent = t("checking");
  notice.hidden = true;
  try {
    const quote = await quoteCart();
    if (request !== epoch) return;
    current = quote;
    render(quote);
    if (quoteFingerprint(quote) !== previous) {
      notice.textContent = t("updatedPrice");
      notice.hidden = false;
      return;
    }
    if (!quote.whatsapp_url) {
      notice.textContent = t("whatsappMissing");
      notice.hidden = false;
      return;
    }
    location.assign(quote.whatsapp_url);
  } catch (error) {
    if (request !== epoch) return;
    current = null;
    render(null, unavailableIds(error));
    showError(notice, error, locale);
  } finally {
    busy = false;
    items.inert = false;
    label.textContent = t("continueWhatsApp");
    whatsapp.disabled = !current?.whatsapp_url;
  }
});
bindDialogs(dialog);
syncFloating();
