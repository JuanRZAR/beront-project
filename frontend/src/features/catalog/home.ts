import { reducedMotion } from "../../shared/components/motion";

const root = document.querySelector<HTMLElement>("[data-home-carousel]");
if (root) {
  const slides = [...root.querySelectorAll<HTMLElement>("[data-home-slide]")];
  const dots = [...root.querySelectorAll<HTMLButtonElement>("[data-home-dot]")];
  const toggle = root.querySelector<HTMLButtonElement>("[data-home-toggle]");
  let index = 0,
    playing = !reducedMotion(),
    hovering = false,
    timer = 0;
  const schedule = () => {
    window.clearTimeout(timer);
    root.removeAttribute("data-running");
    if (!toggle) return;
    toggle.disabled = reducedMotion();
    toggle.setAttribute(
      "aria-label",
      (playing ? root.dataset.pauseLabel : root.dataset.playLabel)!,
    );
    toggle.setAttribute("aria-pressed", String(!playing));
    toggle.querySelector<HTMLElement>("[data-home-pause]")!.hidden = !playing;
    toggle.querySelector<HTMLElement>("[data-home-play]")!.hidden = playing;
    root.toggleAttribute("data-playing", playing && !reducedMotion());
    root
      .querySelector("[data-home-slides]")
      ?.setAttribute("aria-live", playing ? "off" : "polite");
    if (
      playing &&
      !hovering &&
      !reducedMotion() &&
      !document.hidden &&
      slides.length > 1
    ) {
      void root.offsetWidth;
      root.setAttribute("data-running", "");
      timer = window.setTimeout(() => show(index + 1), 7000);
    }
  };
  const show = (next: number, manual = false) => {
    if (manual) playing = false;
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      slide.toggleAttribute("data-active", i === index);
      slide.inert = i !== index;
      slide.setAttribute("aria-hidden", String(i !== index));
    });
    dots.forEach((dot, i) => {
      if (i === index) dot.setAttribute("aria-current", "true");
      else dot.removeAttribute("aria-current");
    });
    const count = root.querySelector("[data-home-count]");
    if (count) count.textContent = `${index + 1} / ${slides.length}`;
    if (manual) {
      const announce = root.querySelector("[data-home-announce]");
      if (announce)
        announce.textContent = slides[index]!.getAttribute("aria-label");
    }
    schedule();
  };
  root
    .querySelector("[data-home-prev]")
    ?.addEventListener("click", () => show(index - 1, true));
  root
    .querySelector("[data-home-next]")
    ?.addEventListener("click", () => show(index + 1, true));
  dots.forEach((dot, i) => dot.addEventListener("click", () => show(i, true)));
  toggle?.addEventListener("click", () => {
    playing = !playing;
    schedule();
  });
  root.addEventListener("keydown", (event) => {
    const next = {
      ArrowLeft: index - 1,
      ArrowRight: index + 1,
      Home: 0,
      End: slides.length - 1,
    }[event.key];
    if (next === undefined) return;
    event.preventDefault();
    show(next, true);
  });
  root.addEventListener("focusin", (event) => {
    if (event.target !== toggle) {
      playing = false;
      schedule();
    }
  });
  root.addEventListener("mouseenter", () => {
    hovering = true;
    schedule();
  });
  root.addEventListener("mouseleave", () => {
    hovering = false;
    schedule();
  });
  document.addEventListener("visibilitychange", schedule);
  const motion = () => {
    if (reducedMotion()) playing = false;
    schedule();
  };
  window.addEventListener("beront:a11y", motion);
  matchMedia("(prefers-reduced-motion: reduce)").addEventListener(
    "change",
    motion,
  );
  schedule();
}
