import { cart } from "../cart/store";
import { requestQuote } from "../cart/quote";
import { translate, money, type Locale } from "../../shared/i18n";
import { toast } from "../../shared/components/toast";
import { flyToCart } from "../../shared/components/motion";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
export function addVariant(
  variantId: string,
  source: HTMLElement,
  image?: string,
) {
  try {
    cart.add(variantId, 1);
  } catch {
    toast(t("limit"));
    return false;
  }
  flyToCart(source, image);
  return true;
}
export function bindSummary(node: HTMLElement | null) {
  if (!node) return;
  const summary = node;
  let epoch = 0;
  async function refresh() {
    const count = cart.read().reduce((sum, item) => sum + item.quantity, 0);
    summary.hidden = count === 0;
    summary.querySelector("[data-summary-text]")!.textContent =
      count === 1
        ? t("summaryOne")
        : t("summaryMany").replace("{n}", String(count));
    if (!count) return;
    const request = ++epoch,
      total = summary.querySelector("[data-summary-total]")!;
    try {
      const quote = await requestQuote(locale);
      if (request === epoch) total.textContent = money(quote.total);
    } catch {
      if (request === epoch) total.textContent = "—";
    }
  }
  window.addEventListener("beront:cart", () => void refresh());
  window.addEventListener("storage", () => {
    cart.invalidate();
    void refresh();
  });
  void refresh();
}
