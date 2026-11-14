import { ApiError, showError } from "../../shared/http/errors";
import type { Quote, QuoteLine } from "../../shared/http/contracts";
import { translate, money, number, type Locale } from "../../shared/i18n";
import { createStepper } from "../../shared/components/stepper";
import { toast } from "../../shared/components/toast";
import { bindDialogs, byId, el } from "../../shared/components/dom";
import {
  levelFor,
  miniVial,
  photoColor,
  vivid,
  css,
  FALLBACK,
  type Rgb,
} from "../../shared/components/vial";
import { cart } from "./store";
import { requestQuote, quoteFingerprint } from "./quote";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const dialog = byId<HTMLDialogElement>("cart-dialog"),
  status = byId("cart-status"),
  notice = byId("cart-notice"),
  items = byId("cart-items"),
  summary = byId("cart-summary"),
  whatsapp = byId<HTMLButtonElement>("continue-whatsapp");
let current: Quote | null = null,
  epoch = 0,
  busy = false,
  origin: HTMLElement | null = null;
const remembered = new Map<string, QuoteLine>();
const colors = new Map<string, Rgb>();
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
    active.dataset.step ??
      ("size" in active.dataset
        ? "size"
        : active.matches("input")
          ? "input"
          : "remove"),
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
        : key[1] === "size"
          ? '[data-size][aria-pressed="true"]'
          : `[data-step="${key[1]}"]`,
  );
  if (target && !target.disabled) target.focus();
  else (row?.querySelector("input") ?? byId("cart-title")).focus();
}
function productVisual(line?: QuoteLine) {
  const visual = el("div", undefined, { class: "cart-row-visual" }),
    missing = el("span", line ? t("imageUnavailable") : "", {
      class: "cart-photo-missing hint",
    });
  if (line?.image_url) {
    const photo = document.createElement("img");
    photo.className = "cart-product-photo";
    photo.alt = `${line.brand_name} ${line.product_name}`;
    photo.decoding = "async";
    photo.addEventListener("error", () => photo.replaceWith(missing), {
      once: true,
    });
    photo.src = line.image_url;
    visual.append(photo);
  } else visual.append(missing);
  if (line?.kind === "decant") {
    visual.classList.add("has-decant");
    const largest = Math.max(
      Number(line.volume_ml),
      ...(line.options ?? []).map((option) => Number(option.volume_ml)),
    );
    const vial = miniVial(levelFor(Number(line.volume_ml), largest), FALLBACK);
    visual.append(vial);
    const url = line.image_url;
    if (url)
      void (
        colors.has(url)
          ? Promise.resolve(colors.get(url)!)
          : photoColor(url).then((color) => colors.set(url, color).get(url)!)
      ).then((color) => vial.style.setProperty("--liquid", css(vivid(color))));
  }
  return visual;
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
      const name = line ? line.product_name : t("productUnavailable");
      const options = line?.options ?? [];
      const main = el("div", undefined, { class: "cart-row-main" });
      main.append(
        el("small", line ? line.brand_name : "", { class: "cart-row-brand" }),
        el("strong", name),
        el(
          "p",
          line
            ? t(line.kind === "decant" ? "decant" : "fullBottle") +
                " · " +
                number(line.volume_ml) +
                " ml"
            : "",
          { class: "hint" },
        ),
      );
      if (line && options.length > 1) {
        const sizes = el("div", undefined, {
          class: "cart-row-sizes",
          role: "group",
          "aria-label": t("changeSize") + " " + name,
        });
        for (const option of options) {
          const pressed = option.variant_id === item.variant_id;
          const pill = el("button", number(option.volume_ml) + " ml", {
            type: "button",
            "data-size": "",
            "aria-pressed": String(pressed),
          });
          pill.addEventListener("click", () => {
            if (pressed) return;
            try {
              cart.replace(item.variant_id, option.variant_id);
            } catch {
              toast(t("limit"));
              return;
            }
            render(quote, unavailable);
            void load();
          });
          sizes.append(pill);
        }
        main.append(sizes);
      }
      if (unavailable.has(item.variant_id))
        main.append(el("p", t("lineUnavailable"), { class: "danger-text" }));
      main.append(
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
      );
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
      const side = el("div", undefined, { class: "cart-row-side" });
      side.append(
        el("strong", quote && line ? money(line.line_total) : "—", {
          class: "cart-row-total",
        }),
        remove,
      );
      row.append(productVisual(line), main, side);
      return row;
    }),
  );
  byId("cart-total").textContent = quote ? money(quote.total) : "—";
  summary.hidden = !quote || !lines.length;
  whatsapp.disabled = !quote?.whatsapp_url;
  byId("whatsapp-unavailable").hidden = !quote || !!quote.whatsapp_url;
  restoreFocus(key);
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
    const quote = await requestQuote(locale);
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
  if (origin?.isConnected) origin.focus({ preventScroll: true });
});
window.addEventListener("storage", () => {
  cart.invalidate();
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
    const quote = await requestQuote(locale);
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
