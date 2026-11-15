export function reducedMotion() {
  return document.documentElement.dataset.motion === "reduce";
}
export function animateNumber(
  node: HTMLElement,
  from: number,
  to: number,
  format: (value: number) => string,
  duration = 420,
) {
  if (reducedMotion() || from === to) {
    node.textContent = format(to);
    return;
  }
  const start = performance.now();
  const step = (now: number) => {
    const progress = Math.min(1, (now - start) / duration);
    node.textContent = format(from + (to - from) * (1 - (1 - progress) ** 3));
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
export function flyToCart(source: HTMLElement, imageUrl?: string) {
  const target = document.querySelector<HTMLElement>(".cart-link");
  if (reducedMotion() || !target) return;
  const from = source.getBoundingClientRect(),
    to = target.getBoundingClientRect(),
    size = imageUrl ? 40 : 14,
    dot = imageUrl
      ? document.createElement("img")
      : document.createElement("i");
  if (dot instanceof HTMLImageElement) {
    dot.src = imageUrl!;
    dot.alt = "";
  }
  dot.setAttribute("aria-hidden", "true");
  dot.className = "fly-dot";
  dot.style.width = dot.style.height = size + "px";
  dot.style.left = from.left + from.width / 2 - size / 2 + "px";
  dot.style.top = from.top + from.height / 2 - size / 2 + "px";
  document.body.append(dot);
  const dx = to.left + to.width / 2 - (from.left + from.width / 2),
    dy = to.top + to.height / 2 - (from.top + from.height / 2);
  dot
    .animate(
      [
        { transform: "translate(0,0) scale(1)" },
        {
          transform: `translate(${dx * 0.5}px,${dy * 0.5 - 80}px) scale(1.2)`,
          offset: 0.5,
        },
        { transform: `translate(${dx}px,${dy}px) scale(.35)` },
      ],
      { duration: 750, easing: "cubic-bezier(.5,0,.3,1)" },
    )
    .addEventListener("finish", () => dot.remove());
}
