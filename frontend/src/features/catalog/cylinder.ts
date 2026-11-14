import { parsePerfume, type Perfume } from "./perfume";
import { itemPlacement, wrapDistance } from "./cylinder-layout";
import { addVariant, bindSummary } from "./summary";
import { bindLiveFilters } from "./liveFilters";
import { translate, money, number, type Locale } from "../../shared/i18n";
import { animateNumber, reducedMotion } from "../../shared/components/motion";
import { FALLBACK, css, photoColor, vivid } from "../../shared/components/vial";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const root = document.querySelector<HTMLElement>("[data-cylinder]");
if (root) init(root);
function init(root: HTMLElement) {
  const q = <T extends HTMLElement>(selector: string) =>
    root.querySelector<T>(selector)!;
  const cyl = q("[data-cyl]"),
    ghost = q("[data-ghost]"),
    thumbsBox = q("[data-thumbs]"),
    sizesBox = q("[data-sizes]"),
    price = q("[data-price]"),
    add = root.querySelector<HTMLButtonElement>("[data-add]"),
    addLabel = root.querySelector<HTMLElement>("[data-add-label]"),
    link = q<HTMLAnchorElement>("[data-link]"),
    announce = q("[data-announce]"),
    prev = q<HTMLButtonElement>("[data-prev]"),
    next = q<HTMLButtonElement>("[data-next]");
  let perfumes: (Perfume | null)[] = [],
    current = 0,
    chosen = 0,
    shownPrice = 0,
    first = true;
  const items = () => [...cyl.querySelectorAll<HTMLElement>(".cyl-item")];
  const thumbs = () => [
    ...thumbsBox.querySelectorAll<HTMLButtonElement>(".cyl-thumb"),
  ];
  const count = () => perfumes.length;
  const textContext = document.createElement("canvas").getContext("2d");
  function fitGhost() {
    const row = ghost.firstElementChild as HTMLElement | null;
    if (!row?.clientWidth || !textContext) return;
    textContext.font = `italic 500 100px ${getComputedStyle(ghost).fontFamily}`;
    const measured = textContext.measureText(row.textContent ?? "").width;
    if (!measured) return;
    const size = Math.min(
      144,
      window.innerWidth * 0.09,
      ghost.clientHeight / 3 / 1.15,
      (row.clientWidth * 94) / measured,
    );
    ghost.style.setProperty("--pattern-size", `${size}px`);
  }
  const spread = () =>
    parseFloat(getComputedStyle(cyl).getPropertyValue("--spread")) || 0.96;
  function layout() {
    const list = items(),
      gap = (list[0]?.offsetWidth ?? 0) * spread();
    list.forEach((item, index) => {
      const place = itemPlacement(wrapDistance(index, current, count()), gap);
      item.style.transform = place.transform;
      item.style.opacity = place.visible ? "1" : "0";
      item.style.pointerEvents = place.visible ? "auto" : "none";
      item.style.zIndex = String(place.layer);
      item.toggleAttribute("data-active", index === current);
    });
    thumbs().forEach((thumb, index) => {
      if (index === current) thumb.setAttribute("aria-current", "true");
      else thumb.removeAttribute("aria-current");
    });
    const active = thumbs()[current];
    if (active)
      thumbsBox.scrollTo({
        left:
          active.offsetLeft - (thumbsBox.clientWidth - active.offsetWidth) / 2,
        behavior: reducedMotion() || first ? "auto" : "smooth",
      });
  }
  function paintSize() {
    const perfume = perfumes[current],
      size = perfume?.variants[chosen];
    if (!perfume || !size) return;
    [...sizesBox.children].forEach((button, index) =>
      button.setAttribute("aria-pressed", String(index === chosen)),
    );
    const target = Number(size.price);
    animateNumber(price, shownPrice, target, (value) =>
      money(value.toFixed(2)),
    );
    shownPrice = target;
    if (add && addLabel) {
      add.disabled = !size.available;
      addLabel.textContent = t(size.available ? "quickAdd" : "soldOut");
    }
    announce.textContent =
      t("slideOf")
        .replace("{n}", String(current + 1))
        .replace("{total}", String(count())) +
      `: ${perfume.brand} ${perfume.name}, ${number(size.volume)} ml, ${money(size.price)}`;
  }
  function render() {
    const perfume = perfumes[current];
    root.classList.toggle("is-empty", !perfume);
    if (!perfume) return;
    q("[data-meta]").textContent =
      perfume.brand + (perfume.category ? " · " + perfume.category : "");
    q("[data-name]").textContent = perfume.name;
    q("[data-kind]").textContent = t("fullBottle") + " · " + perfume.audience;
    link.href = `/${locale}/products/${encodeURIComponent(perfume.slug)}?kind=full_bottle`;
    link.hidden = false;
    sizesBox.replaceChildren();
    perfume.variants.forEach((size, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "size-button";
      const volume = document.createElement("strong");
      volume.textContent = number(size.volume) + " ml";
      button.append(volume);
      button.addEventListener("click", () => {
        chosen = index;
        paintSize();
      });
      sizesBox.append(button);
    });
    const available = perfume.variants.findIndex((size) => size.available);
    chosen = Math.max(0, available);
    ghost.querySelectorAll("span").forEach((row) => {
      row.textContent = perfume.name;
    });
    fitGhost();
    paintSize();
    layout();
    void photoColor(perfume.image?.url ?? null).then((color) => {
      if (perfumes[current] === perfume)
        root.style.setProperty("--glow", css(vivid(color ?? FALLBACK), 0.32));
    });
    const url = new URL(location.href);
    url.searchParams.set("selected", perfume.slug);
    history.replaceState(null, "", url);
    first = false;
  }
  function go(index: number) {
    if (!count()) return;
    current = ((index % count()) + count()) % count();
    render();
  }
  function setup() {
    perfumes = items().map((item) => parsePerfume(item.dataset.product));
    const slug = new URL(location.href).searchParams.get("selected"),
      found = perfumes.findIndex((perfume) => perfume?.slug === slug),
      preferred = perfumes.findIndex((perfume) =>
        perfume?.variants.some((size) => size.available),
      );
    current = found >= 0 ? found : Math.max(0, preferred);
    first = true;
    prev.disabled = next.disabled = count() < 2;
    items().forEach((item, index) =>
      item.addEventListener("click", () => {
        if (!moved && index !== current) go(index);
      }),
    );
    thumbs().forEach((thumb, index) =>
      thumb.addEventListener("click", () => go(index)),
    );
    render();
  }
  prev.addEventListener("click", () => go(current - 1));
  next.addEventListener("click", () => go(current + 1));
  root.addEventListener("keydown", (event) => {
    const target = event.target as HTMLElement;
    if (target.closest("input, select, textarea, details")) return;
    if (event.key === "ArrowRight") go(current + 1);
    if (event.key === "ArrowLeft") go(current - 1);
  });
  /* Arrastre */
  let startX = 0,
    dragging = false,
    moved = false;
  cyl.addEventListener("pointerdown", (event) => {
    dragging = true;
    moved = false;
    startX = event.clientX;
  });
  window.addEventListener("pointermove", (event) => {
    if (dragging && Math.abs(event.clientX - startX) > 8) moved = true;
  });
  window.addEventListener("pointerup", (event) => {
    if (!dragging) return;
    dragging = false;
    const delta = event.clientX - startX;
    if (Math.abs(delta) > 50) go(current + (delta < 0 ? 1 : -1));
    window.setTimeout(() => (moved = false), 0);
  });
  new ResizeObserver(() => {
    layout();
    fitGhost();
  }).observe(cyl);
  void document.fonts.ready.then(fitGhost);
  /* Agregar */
  add?.addEventListener("click", () => {
    const perfume = perfumes[current],
      size = perfume?.variants[chosen];
    if (!add || !addLabel || !perfume || !size?.available) return;
    if (!addVariant(size.id, add, perfume.image?.url)) return;
    addLabel.textContent = t("added");
    add.disabled = true;
    window.setTimeout(paintSize, 1400);
  });
  bindSummary(root.querySelector<HTMLElement>("[data-summary]"));
  /* Filtros sin recargar */
  bindLiveFilters({
    root,
    form: q<HTMLFormElement>("#cylinder-filters"),
    regions: ["[data-cyl]", "[data-thumbs]", "[data-results]"],
    selected: () => perfumes[current]?.slug,
    onSwap: setup,
  });
  setup();
}
