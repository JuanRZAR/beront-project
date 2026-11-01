const POINTS: [number, number][] = [
  [0.02, 0.02],
  [0.98, 0.02],
  [0.02, 0.98],
  [0.98, 0.98],
  [0.08, 0.08],
  [0.92, 0.08],
  [0.08, 0.92],
  [0.92, 0.92],
];
function harmonize(img: HTMLImageElement) {
  try {
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 1;
    const context = canvas.getContext("2d", { willReadFrequently: true })!;
    const tones: number[] = [];
    for (const [x, y] of POINTS) {
      context.clearRect(0, 0, 1, 1);
      context.drawImage(
        img,
        Math.floor((img.naturalWidth - 1) * x),
        Math.floor((img.naturalHeight - 1) * y),
        1,
        1,
        0,
        0,
        1,
        1,
      );
      const [r = 0, g = 0, b = 0, a = 0] = context.getImageData(
        0,
        0,
        1,
        1,
      ).data;
      if (
        a > 245 &&
        Math.max(r, g, b) - Math.min(r, g, b) < 20 &&
        Math.min(r, g, b) > 175
      )
        tones.push(Math.min(r, g, b));
    }
    if (tones.length >= 4) {
      tones.sort((a, b) => a - b);
      const tone = tones[Math.floor(tones.length / 3)] ?? 255;
      img.style.setProperty(
        "--photo-light",
        String(Math.min(1.45, 255 / tone)),
      );
    }
  } catch {
    // Same-origin pixel access can still be restricted; CSS blending remains.
  }
}
export function harmonizePhotos(root: ParentNode = document) {
  root.querySelectorAll<HTMLImageElement>("img[data-photo]").forEach((img) => {
    if (img.complete && img.naturalWidth) harmonize(img);
    else img.addEventListener("load", () => harmonize(img), { once: true });
  });
}
