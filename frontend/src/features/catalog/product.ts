import { cart } from "../cart/store";
import { translate, money, type Locale } from "../../shared/i18n";
import type { Variant } from "../../shared/http/contracts";
import { mediaUrl } from "../../shared/http/serialization";
import { toast } from "../../shared/components/toast";
import { harmonizePhotos } from "../../shared/components/photos";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const data = document.getElementById("product-data")?.textContent;
if (data) {
  const { variants, selected } = JSON.parse(data) as {
    variants: Variant[];
    selected?: string;
  };
  let current = variants.find((v) => v.id === selected);
  const button = document.querySelector<HTMLButtonElement>("#add-to-cart");
  const quantity =
    document.querySelector<HTMLInputElement>("#product-quantity");
  document.querySelectorAll<HTMLButtonElement>("[data-variant]").forEach((el) =>
    el.addEventListener("click", () => {
      current = variants.find((v) => v.id === el.dataset.variant);
      if (!current || !button) return;
      document
        .querySelectorAll("[data-variant]")
        .forEach((node) =>
          node.setAttribute("aria-pressed", String(node === el)),
        );
      document.getElementById("detail-price")!.textContent =
        money(current.price) + " USD";
      document.getElementById("variant-status")!.textContent = t(
        current.available ? "available" : "soldOut",
      );
      button.disabled = !current.available;
      button.querySelector("span")!.textContent = t(
        current.available ? "addCart" : "soldOut",
      );
    }),
  );
  document
    .querySelectorAll<HTMLButtonElement>("[data-product-quantity]")
    .forEach((el) =>
      el.addEventListener("click", () => {
        if (quantity)
          quantity.value = String(
            Math.max(
              1,
              Math.min(
                20,
                Number(quantity.value) + Number(el.dataset.productQuantity),
              ),
            ),
          );
      }),
    );
  button?.addEventListener("click", () => {
    if (!current || !current.available || !quantity?.reportValidity()) return;
    try {
      cart.add(current.id, Number(quantity.value));
      window.dispatchEvent(
        new CustomEvent("beront:open-cart", { detail: button }),
      );
      if (!cart.persistent) {
        const notice = document.getElementById("storage-notice")!;
        notice.textContent = t("storageUnavailable");
        notice.hidden = false;
      }
    } catch {
      toast(t("limit"));
    }
  });
  document.querySelectorAll<HTMLButtonElement>("[data-photo]").forEach((el) =>
    el.addEventListener("click", () => {
      const src = mediaUrl(el.dataset.photo ?? ""),
        image = document.querySelector<HTMLImageElement>(
          "#product-gallery img",
        );
      if (src && image) {
        image.src = src;
        image.alt = el.dataset.photoAlt ?? "";
      }
    }),
  );
}
harmonizePhotos();
