interface Options {
  root: HTMLElement;
  form: HTMLFormElement;
  regions: string[];
  selected: () => string | undefined;
  onSwap: () => void;
}
const withoutSelected = (url: URL) => {
  const copy = new URL(url);
  copy.searchParams.delete("selected");
  return copy.search;
};
export function bindLiveFilters({
  root,
  form,
  regions,
  selected,
  onSwap,
}: Options) {
  let loaded = withoutSelected(new URL(location.href)),
    epoch = 0,
    timer = 0;
  let controller: AbortController | undefined;
  function filterUrl(page?: string) {
    const url = new URL(location.pathname, location.origin);
    for (const [key, value] of new FormData(form))
      if (typeof value === "string" && value.trim())
        url.searchParams.append(key, value.trim());
    if (page) url.searchParams.set("page", page);
    return url;
  }
  async function load(url: URL) {
    if (withoutSelected(url) === loaded) return;
    loaded = withoutSelected(url);
    const request = ++epoch;
    controller?.abort();
    controller = new AbortController();
    const signal = controller.signal;
    root.setAttribute("aria-busy", "true");
    try {
      const response = await fetch(url, {
        headers: { Accept: "text/html" },
        signal,
      });
      if (!response.ok) throw new Error("response");
      const html = new DOMParser().parseFromString(
        await response.text(),
        "text/html",
      );
      if (request !== epoch) return;
      const fresh = regions.map((selector) => html.querySelector(selector));
      if (fresh.some((node) => !node)) throw new Error("region");
      regions.forEach((selector, index) =>
        root
          .querySelector(selector)!
          .replaceChildren(...fresh[index]!.childNodes),
      );
      const slug = selected();
      if (slug) url.searchParams.set("selected", slug);
      history.replaceState(null, "", url);
      onSwap();
    } catch {
      if (request !== epoch || signal.aborted) return;
      location.assign(url);
    } finally {
      if (request === epoch) root.removeAttribute("aria-busy");
    }
  }
  const run = (page?: string) => {
    if (form.reportValidity()) void load(filterUrl(page));
  };
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    run();
  });
  form.addEventListener("change", () => run());
  form
    .querySelector<HTMLInputElement>('input[name="q"]')
    ?.addEventListener("input", () => {
      clearTimeout(timer);
      timer = window.setTimeout(() => run(), 350);
    });
  form.querySelector("[data-clear]")?.addEventListener("click", (event) => {
    event.preventDefault();
    location.assign((event.currentTarget as HTMLAnchorElement).href);
  });
  root.addEventListener("click", (event) => {
    const link = (event.target as HTMLElement).closest<HTMLAnchorElement>(
      ".pagination a",
    );
    if (!link) return;
    event.preventDefault();
    run(new URL(link.href).searchParams.get("page") ?? "1");
  });
}
