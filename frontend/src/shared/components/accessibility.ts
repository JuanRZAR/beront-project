import { reducedMotion } from "./motion";
const KEY = "beront.a11y.v1";
type Text = "large" | "xlarge" | undefined;
interface Saved {
  text?: Text;
  contrast?: "high";
  motion?: "reduce" | "full";
}
const root = document.documentElement;
function read(): Saved {
  try {
    const value = JSON.parse(localStorage.getItem(KEY) ?? "{}");
    return value && typeof value === "object" ? value : {};
  } catch {
    return {};
  }
}
function apply(next: Saved) {
  if (next.contrast === "high") root.dataset.contrast = "high";
  else delete root.dataset.contrast;
  if (next.text) root.dataset.text = next.text;
  else delete root.dataset.text;
  if (next.motion) root.dataset.motion = next.motion;
  else delete root.dataset.motion;
}
function save(next: Saved) {
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    // The preference still applies until the page closes.
  }
  apply(next);
  paint();
  window.dispatchEvent(new Event("beront:a11y"));
}
const panel = document.getElementById("a11y-panel");
function paint() {
  if (!panel) return;
  const text = root.dataset.text ?? "";
  panel
    .querySelectorAll<HTMLButtonElement>("[data-text]")
    .forEach((button) =>
      button.setAttribute(
        "aria-pressed",
        String((button.dataset.text ?? "") === text),
      ),
    );
  panel.querySelector<HTMLInputElement>("[data-contrast]")!.checked =
    root.dataset.contrast === "high";
  panel.querySelector<HTMLInputElement>("[data-motion]")!.checked =
    reducedMotion();
}
panel?.querySelectorAll<HTMLButtonElement>("[data-text]").forEach((button) =>
  button.addEventListener("click", () => {
    const text = button.dataset.text as Text | "";
    save({ ...read(), text: text || undefined });
  }),
);
panel
  ?.querySelector<HTMLInputElement>("[data-contrast]")
  ?.addEventListener("change", (event) =>
    save({
      ...read(),
      contrast: (event.target as HTMLInputElement).checked ? "high" : undefined,
    }),
  );
panel
  ?.querySelector<HTMLInputElement>("[data-motion]")
  ?.addEventListener("change", (event) => {
    const requested = (event.target as HTMLInputElement).checked;
    save({
      ...read(),
      motion: requested ? "reduce" : "full",
    });
  });
panel
  ?.querySelector("[data-a11y-reset]")
  ?.addEventListener("click", () => save({}));
apply(read());
paint();
