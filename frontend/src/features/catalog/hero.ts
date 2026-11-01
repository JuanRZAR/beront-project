import { harmonizePhotos } from "../../shared/components/photos";
const region = document.querySelector<HTMLElement>("#hero-carousel");
if (region) {
  const slides = [...region.querySelectorAll<HTMLElement>("[data-slide]")],
    dots = [...region.querySelectorAll<HTMLButtonElement>("[data-dot]")],
    announce = region.querySelector<HTMLElement>("#carousel-announcement")!;
  let index = 0;
  const show = (next: number, announceChange = true) => {
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, position) => (slide.hidden = position !== index));
    dots.forEach((dot, position) =>
      dot.setAttribute("aria-current", String(position === index)),
    );
    const active = slides[index]!;
    harmonizePhotos(active);
    if (announceChange)
      announce.textContent =
        `${index + 1} / ${slides.length}: ` + (active.dataset.label ?? "");
  };
  region
    .querySelector("#carousel-previous")
    ?.addEventListener("click", () => show(index - 1));
  region
    .querySelector("#carousel-next")
    ?.addEventListener("click", () => show(index + 1));
  dots.forEach((dot, position) =>
    dot.addEventListener("click", () => show(position)),
  );
  region.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    event.preventDefault();
    show(index + (event.key === "ArrowRight" ? 1 : -1));
  });
  let start: Touch | undefined;
  region.addEventListener(
    "touchstart",
    (event) => {
      start = event.changedTouches[0];
    },
    { passive: true },
  );
  region.addEventListener(
    "touchend",
    (event) => {
      const end = event.changedTouches[0];
      if (!start || !end) return;
      const dx = end.clientX - start.clientX,
        dy = end.clientY - start.clientY;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy))
        show(index + (dx < 0 ? 1 : -1));
      start = undefined;
    },
    { passive: true },
  );
  show(0, false);
}
