import { addVariant, bindSummary } from "./summary";
import { bindLiveFilters } from "./liveFilters";
import { translate, money, number, type Locale } from "../../shared/i18n";
import { parsePerfume, type Perfume } from "./perfume";
import { animateNumber, reducedMotion } from "../../shared/components/motion";
import {
  FALLBACK,
  css,
  levelFor,
  photoColor,
  vivid,
} from "../../shared/components/vial";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const root = document.querySelector<HTMLElement>("[data-studio]");
if (root) init(root);
function init(root: HTMLElement) {
  const q = <T extends HTMLElement>(selector: string) =>
    root.querySelector<T>(selector)!;
  const scene = root.querySelector<HTMLElement>(".studio-scene")!,
    liquid = root.querySelector<SVGGElement>("[data-liquid]")!,
    vial = q("[data-vial]"),
    ticks = q("[data-ticks]"),
    photo = q<HTMLImageElement>("[data-scene-photo]"),
    sizesBox = q("[data-sizes]"),
    price = q("[data-scene-price]"),
    add = root.querySelector<HTMLButtonElement>("[data-add]"),
    addLabel = root.querySelector<HTMLElement>("[data-add-label]"),
    announce = q("[data-announce]"),
    form = q<HTMLFormElement>("#studio-filters"),
    summary = root.querySelector<HTMLElement>("[data-summary]");
  let current: Perfume | null = null,
    chosen = 0,
    shownPrice = 0,
    swapTimer = 0;
  const yOf = (level: number) => 410 - level * 320;
  const largest = () =>
    Math.max(...current!.variants.map((size) => Number(size.volume)));
  const levelOf = (index: number) =>
    levelFor(Number(current!.variants[index]!.volume), largest());
  function tint(color = FALLBACK) {
    const accent = vivid(color);
    scene.style.setProperty("--liquid", css(accent));
    root.style.setProperty("--glow", css(accent, 0.32));
  }
  function paintSize() {
    if (!current) return;
    const size = current.variants[chosen];
    [...sizesBox.children].forEach((button, index) =>
      button.setAttribute("aria-pressed", String(index === chosen)),
    );
    [...ticks.children].forEach((button, index) =>
      button.setAttribute("aria-pressed", String(index === chosen)),
    );
    if (!size) return;
    const next = Number(size.price);
    animateNumber(price, shownPrice, next, (value) => money(value.toFixed(2)));
    shownPrice = next;
    liquid.style.setProperty("--drop", yOf(levelOf(chosen)) + "px");
    if (add && addLabel) {
      add.disabled = !size.available;
      addLabel.textContent = t(size.available ? "quickAdd" : "soldOut");
    }
    announce.textContent = `${current.brand} ${current.name}, ${number(size.volume)} ml, ${money(size.price)}`;
  }
  function chooseSize(index: number) {
    chosen = index;
    paintSize();
  }
  function buildSizes() {
    sizesBox.replaceChildren();
    ticks.replaceChildren();
    current!.variants.forEach((size, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "size-button";
      const volume = document.createElement("strong"),
        amount = document.createElement("small");
      volume.textContent = number(size.volume) + " ml";
      amount.textContent = money(size.price);
      button.append(volume, amount);
      button.addEventListener("click", () => chooseSize(index));
      sizesBox.append(button);
      const tick = document.createElement("button");
      tick.type = "button";
      tick.className = "vial-tick";
      tick.tabIndex = -1;
      tick.textContent = number(size.volume) + " ml";
      tick.style.top = (yOf(levelOf(index)) / 420) * 100 + "%";
      tick.addEventListener("click", () => chooseSize(index));
      ticks.append(tick);
    });
  }
  function select(card: HTMLElement, user: boolean) {
    const perfume = parsePerfume(card.dataset.product);
    if (!perfume) return;
    const first = current === null;
    current = perfume;
    scene.hidden = false;
    root.dataset.hasSelection = "true";
    root
      .querySelectorAll<HTMLElement>(".studio-card")
      .forEach((item) =>
        item.setAttribute("aria-pressed", String(item === card)),
      );
    q("[data-scene-meta]").textContent =
      perfume.brand + (perfume.category ? " · " + perfume.category : "");
    q("[data-scene-name]").textContent = perfume.name;
    q("[data-scene-kind]").textContent =
      t("decants") + " · " + perfume.audience;
    const link = q<HTMLAnchorElement>("[data-scene-link]");
    link.href = `/${locale}/products/${encodeURIComponent(perfume.slug)}?kind=decant`;
    link.hidden = false;
    photo.classList.add("is-swapping");
    window.setTimeout(
      () => {
        if (perfume.image) {
          photo.src = perfume.image.url;
          photo.alt = perfume.image.alt;
          photo.hidden = false;
        } else photo.hidden = true;
        photo.parentElement?.toggleAttribute("hidden", !perfume.image);
        photo.classList.remove("is-swapping");
      },
      first || reducedMotion() ? 0 : 180,
    );
    const preferred = Math.min(1, perfume.variants.length - 1);
    chosen = perfume.variants[preferred]?.available
      ? preferred
      : Math.max(
          0,
          perfume.variants.findIndex((size) => size.available),
        );
    buildSizes();
    clearTimeout(swapTimer);
    const apply = () => {
      void photoColor(perfume.image?.url ?? null).then((color) => {
        if (current === perfume) tint(color);
      });
      paintSize();
    };
    if (first || reducedMotion()) apply();
    else {
      liquid.style.setProperty("--drop", "430px");
      swapTimer = window.setTimeout(apply, 520);
    }
    const url = new URL(location.href);
    url.searchParams.set("selected", perfume.slug);
    history.replaceState(null, "", url);
    if (user && window.innerWidth < 840)
      scene.scrollIntoView({
        behavior: reducedMotion() ? "auto" : "smooth",
        block: "start",
      });
  }
  /* Arrastre del nivel del frasco */
  let dragging = false;
  function fromPointer(event: PointerEvent) {
    if (!current) return;
    const box = vial.getBoundingClientRect(),
      level = (410 - ((event.clientY - box.top) / box.height) * 420) / 320;
    let best = 0,
      distance = Infinity;
    current.variants.forEach((_, index) => {
      const gap = Math.abs(levelOf(index) - level);
      if (gap < distance) {
        distance = gap;
        best = index;
      }
    });
    if (best !== chosen) chooseSize(best);
  }
  vial.addEventListener("pointerdown", (event) => {
    if ((event.target as HTMLElement).closest(".vial-tick")) return;
    dragging = true;
    vial.setPointerCapture(event.pointerId);
    fromPointer(event);
  });
  vial.addEventListener("pointermove", (event) => {
    if (dragging) fromPointer(event);
  });
  for (const end of ["pointerup", "pointercancel"])
    vial.addEventListener(end, () => (dragging = false));
  /* Agregar */
  add?.addEventListener("click", () => {
    const size = current?.variants[chosen];
    if (!add || !addLabel || !current || !size?.available) return;
    if (!addVariant(size.id, add, current.image?.url)) return;
    addLabel.textContent = t("added");
    add.disabled = true;
    window.setTimeout(paintSize, 1400);
  });
  bindSummary(summary);
  /* Lista y filtros sin recargar la página */
  const results = () => q("[data-results]");
  function bindCards() {
    results()
      .querySelectorAll<HTMLElement>(".studio-card")
      .forEach((card) =>
        card.addEventListener("click", () => select(card, true)),
      );
  }
  function markCurrent() {
    if (!current) return;
    results()
      .querySelectorAll<HTMLElement>(".studio-card")
      .forEach((card) =>
        card.setAttribute(
          "aria-pressed",
          String(parsePerfume(card.dataset.product)?.slug === current!.slug),
        ),
      );
  }
  bindLiveFilters({
    root,
    form,
    regions: ["[data-results]"],
    selected: () => current?.slug,
    onSwap: () => {
      bindCards();
      markCurrent();
    },
  });
  bindCards();
  const start = results().querySelector<HTMLElement>(
    '.studio-card[aria-pressed="true"]',
  );
  if (start) select(start, false);
}
