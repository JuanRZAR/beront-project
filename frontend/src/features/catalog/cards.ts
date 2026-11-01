import { cart } from "../cart/store";
import { translate, money, number, type Locale } from "../../shared/i18n";
import { bindStepper } from "../../shared/components/stepper";
import { harmonizePhotos } from "../../shared/components/photos";
import { toast } from "../../shared/components/toast";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
harmonizePhotos();
document.querySelectorAll<HTMLElement>("[data-card]").forEach((card) => {
  const radios = [
      ...card.querySelectorAll<HTMLInputElement>("input[type=radio]"),
    ],
    price = card.querySelector("[data-card-price]")!,
    size = card.querySelector("[data-card-size]")!,
    stock = card.querySelector<HTMLElement>("[data-card-stock]")!,
    add = card.querySelector<HTMLButtonElement>("[data-card-add]")!,
    label = add.querySelector("span")!,
    stepper = card.querySelector<HTMLElement>("[data-stepper]")!,
    quantity = stepper.querySelector("input")!;
  const sync = () => {
    const selected = radios.find((radio) => radio.checked);
    if (!selected) return;
    const available = selected.dataset.available === "true";
    price.textContent = money(selected.dataset.price ?? "");
    size.textContent = number(selected.dataset.volume ?? "") + " ml";
    stock.hidden = available;
    add.disabled = !available;
    label.textContent = t(available ? "quickAdd" : "soldOut");
  };
  radios.forEach((radio) => radio.addEventListener("change", sync));
  bindStepper(stepper, undefined, () => toast(t("limit")));
  add.addEventListener("click", () => {
    const selected = radios.find((radio) => radio.checked);
    if (!selected || !quantity.reportValidity()) return;
    try {
      cart.add(selected.value, Number(quantity.value));
    } catch {
      toast(t("limit"));
      return;
    }
    window.dispatchEvent(new CustomEvent("beront:open-cart", { detail: add }));
  });
  sync();
});
