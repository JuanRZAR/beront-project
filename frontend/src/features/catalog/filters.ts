const form = document.querySelector<HTMLFormElement>("#catalog-filters");
function submitFilters() {
  if (!form || !form.reportValidity()) return;
  const url = new URL(location.href);
  url.search = "";
  for (const [key, value] of new FormData(form)) {
    if (typeof value === "string" && value.trim())
      url.searchParams.append(key, value.trim());
  }
  location.assign(url.pathname + url.search);
}
form?.addEventListener("submit", (event) => {
  event.preventDefault();
  submitFilters();
});
form?.addEventListener("change", submitFilters);
document
  .querySelector("[data-filter-sort]")
  ?.addEventListener("change", submitFilters);
const openButton = document.querySelector<HTMLButtonElement>("#open-filters");
const closeButton = document.querySelector<HTMLButtonElement>("#close-filters");
const panel = document.querySelector<HTMLElement>("#filters");
openButton?.addEventListener("click", () => {
  panel?.classList.add("is-open");
  openButton.setAttribute("aria-expanded", "true");
  closeButton?.focus();
});
function closePanel() {
  panel?.classList.remove("is-open");
  openButton?.setAttribute("aria-expanded", "false");
  openButton?.focus();
}
closeButton?.addEventListener("click", closePanel);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && panel?.classList.contains("is-open"))
    closePanel();
});
