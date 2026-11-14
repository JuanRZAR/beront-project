export type Rgb = [number, number, number];
export const FALLBACK: Rgb = [184, 165, 138];
export const levelFor = (volume: number, largest: number) =>
  largest > 0 ? 0.2 + 0.7 * Math.min(1, volume / largest) : 0.5;
export function vivid([red, green, blue]: Rgb): Rgb {
  const r = red / 255,
    g = green / 255,
    b = blue / 255,
    max = Math.max(r, g, b),
    min = Math.min(r, g, b),
    delta = max - min;
  let hue = 0,
    saturation = 0;
  const lightness = (max + min) / 2;
  if (delta) {
    saturation =
      lightness > 0.5 ? delta / (2 - max - min) : delta / (max + min);
    hue =
      max === r
        ? (g - b) / delta + (g < b ? 6 : 0)
        : max === g
          ? (b - r) / delta + 2
          : (r - g) / delta + 4;
    hue *= 60;
  }
  const s = Math.min(1, saturation * 1.5 + 0.12),
    l = Math.min(0.6, Math.max(0.42, lightness)),
    a = s * Math.min(l, 1 - l),
    channel = (n: number) => {
      const k = (n + hue / 30) % 12;
      return Math.round(
        255 * (l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1))),
      );
    };
  return [channel(0), channel(8), channel(4)];
}
export function averageColor(img: HTMLImageElement): Rgb | null {
  try {
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 24;
    const context = canvas.getContext("2d", { willReadFrequently: true })!;
    context.drawImage(img, 0, 0, 24, 24);
    const data = context.getImageData(0, 0, 24, 24).data;
    let red = 0,
      green = 0,
      blue = 0,
      weight = 0;
    for (let index = 0; index < data.length; index += 4) {
      const r = data[index]!,
        g = data[index + 1]!,
        b = data[index + 2]!,
        alpha = data[index + 3]! / 255,
        spread = Math.max(r, g, b) - Math.min(r, g, b);
      if (!alpha) continue;
      if (Math.min(r, g, b) > 224) continue;
      const w = (1 + spread / 40) * alpha;
      red += r * w;
      green += g * w;
      blue += b * w;
      weight += w;
    }
    return weight
      ? [
          Math.round(red / weight),
          Math.round(green / weight),
          Math.round(blue / weight),
        ]
      : null;
  } catch {
    return null;
  }
}
export function photoColor(url: string | null): Promise<Rgb> {
  return new Promise((resolve) => {
    if (!url) return resolve(FALLBACK);
    const img = new Image();
    img.onload = () => resolve(averageColor(img) ?? FALLBACK);
    img.onerror = () => resolve(FALLBACK);
    img.src = url;
  });
}
export const css = (color: Rgb, alpha?: number) =>
  `rgb(${color.join(" ")}${alpha === undefined ? "" : " / " + alpha})`;
const SVG = "http://www.w3.org/2000/svg";
let sequence = 0;
export function miniVial(level: number, color: Rgb) {
  const id = "mini-vial-" + ++sequence,
    svg = document.createElementNS(SVG, "svg");
  svg.setAttribute("class", "mini-vial");
  svg.setAttribute("viewBox", "0 0 52 118");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  svg.style.setProperty("--liquid", css(vivid(color)));
  svg.style.setProperty("--drop", String(Math.round((1 - level) * 92)) + "px");
  svg.innerHTML =
    `<defs><clipPath id="${id}"><rect x="8" y="22" width="36" height="92" rx="11"/></clipPath></defs>` +
    `<g clip-path="url(#${id})"><g class="liquid"><g transform="translate(0 18) scale(.26 1)">` +
    `<g class="wave-back"><path d="M0 4 Q25 -4 50 4 T100 4 T150 4 T200 4 T250 4 T300 4 T350 4 T400 4 T450 4 T500 4 V120 H0Z"/></g>` +
    `<g class="wave-front"><path d="M0 4 Q25 -4 50 4 T100 4 T150 4 T200 4 T250 4 T300 4 T350 4 T400 4 T450 4 T500 4 V120 H0Z"/></g>` +
    `</g></g></g>` +
    `<rect class="glass" x="8" y="22" width="36" height="92" rx="11"/>` +
    `<rect class="cap" x="17" y="2" width="18" height="16" rx="4"/>` +
    `<rect class="glass" x="21" y="17" width="10" height="6"/>`;
  return svg;
}
