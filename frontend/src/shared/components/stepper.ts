import type { Locale } from "../i18n";
import { translate } from "../i18n";

const SVG = "http://www.w3.org/2000/svg";
function icon(path: string) {
  const svg = document.createElementNS(SVG, "svg");
  svg.setAttribute("class", "icon");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "1.5");
  svg.setAttribute("aria-hidden", "true");
  const node = document.createElementNS(SVG, "path");
  node.setAttribute("d", path);
  svg.append(node);
  return svg;
}
export function createStepper(
  locale: Locale,
  label: string,
  value: number,
  onChange: (value: number) => void,
  onLimit: () => void,
) {
  const t = translate(locale);
  const group = document.createElement("div");
  group.className = "quantity-stepper";
  const minus = document.createElement("button"),
    plus = document.createElement("button"),
    input = document.createElement("input");
  minus.type = plus.type = "button";
  minus.dataset.step = "-1";
  plus.dataset.step = "1";
  minus.setAttribute("aria-label", t("reduce") + ": " + label);
  plus.setAttribute("aria-label", t("increase") + ": " + label);
  minus.append(icon("M5 12h14"));
  plus.append(icon("M12 5v14M5 12h14"));
  input.type = "number";
  input.inputMode = "numeric";
  input.min = "1";
  input.max = "20";
  input.step = "1";
  input.required = true;
  input.value = String(value);
  input.setAttribute("aria-label", t("quantity") + ": " + label);
  group.append(minus, input, plus);
  bindStepper(group, onChange, onLimit);
  return group;
}
export function bindStepper(
  group: HTMLElement,
  onChange: (value: number) => void = () => {},
  onLimit: () => void = () => {},
) {
  const input = group.querySelector("input")!,
    minus = group.querySelector<HTMLButtonElement>('[data-step="-1"]')!,
    plus = group.querySelector<HTMLButtonElement>('[data-step="1"]')!;
  let value = Number(input.value) || 1;
  const sync = (next: number) => {
    value = next;
    input.value = String(next);
    minus.disabled = next <= 1;
    plus.disabled = next >= 20;
  };
  const change = (next: number) => {
    if (!Number.isInteger(next) || next < 1 || next > 20) {
      sync(value);
      onLimit();
    } else if (next !== value) {
      sync(next);
      onChange(next);
    } else sync(value);
  };
  minus.addEventListener("click", () => change(value - 1));
  plus.addEventListener("click", () => change(value + 1));
  input.addEventListener("change", () => change(Number(input.value)));
  sync(value);
}
