export function el(
  tag: string,
  text?: string,
  attributes: Record<string, string> = {},
) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  for (const [key, value] of Object.entries(attributes))
    node.setAttribute(key, value);
  return node;
}
export function byId<T extends HTMLElement = HTMLElement>(id: string) {
  const node = document.getElementById(id);
  if (!node) throw new Error("Missing element #" + id);
  return node as T;
}
export function formatDate(value: string, locale: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(locale === "en" ? "en-US" : "es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "America/Guayaquil",
  }).format(date);
}
export function slugify(value: string) {
  return value
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 64)
    .replace(/-+$/g, "");
}
export function bindDialogs(root: ParentNode = document) {
  root
    .querySelectorAll<HTMLButtonElement>("[data-close]")
    .forEach((button) =>
      button.addEventListener("click", () => button.closest("dialog")?.close()),
    );
  root
    .querySelectorAll<HTMLDialogElement>("dialog")
    .forEach((dialog) =>
      dialog.addEventListener("close", () =>
        (
          dialog as HTMLDialogElement & { opener?: HTMLElement }
        ).opener?.focus(),
      ),
    );
}
export function openDialog(dialog: HTMLDialogElement, opener?: HTMLElement) {
  (dialog as HTMLDialogElement & { opener?: HTMLElement }).opener =
    opener ?? (document.activeElement as HTMLElement | undefined);
  dialog.showModal();
}
export function setStatus(id: string, text: string) {
  const node = document.getElementById(id);
  if (node) node.textContent = text;
}
