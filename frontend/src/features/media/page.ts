import { api, jsonRequest } from "../../shared/http/client";
import { bindForm } from "../../shared/http/forms";
import { ApiError, errorMessage, showError } from "../../shared/http/errors";
import { translate, type Locale } from "../../shared/i18n";
import {
  bindDialogs,
  byId,
  el,
  openDialog,
  setStatus,
} from "../../shared/components/dom";
import type { MediaAsset, Product } from "../../shared/http/contracts";

const locale: Locale = document.documentElement.lang === "en" ? "en" : "es";
const t = translate(locale);
const PAGE_SIZE = 24;
let page = 1;
let query = "";
let total = 0;
let selected: MediaAsset | null = null;
let assets: MediaAsset[] = [];
let deleteArmed: number | undefined;

const errorBox = byId("media-error");
function show(error: unknown) {
  showError(errorBox, error, locale);
}
function dimensions(asset: MediaAsset) {
  return `${asset.width} × ${asset.height}`;
}
async function load() {
  try {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(PAGE_SIZE),
    });
    if (query) params.set("q", query);
    const result = await api<MediaAsset[]>("/api/v1/admin/media?" + params);
    assets = result.data;
    total = result.meta?.total ?? assets.length;
    errorBox.hidden = true;
  } catch (error) {
    show(error);
    return;
  }
  byId("media-gallery").replaceChildren(
    ...assets.map((asset) => {
      const card = el("button", undefined, {
        type: "button",
        class: "media-card",
        "aria-label": t("openPhoto") + " " + (asset.name || dimensions(asset)),
      });
      card.append(
        el("img", undefined, {
          src: asset.url,
          alt: asset.name,
          loading: "lazy",
        }),
        el("span", asset.name || t("unnamedPhoto")),
        el("small", dimensions(asset)),
      );
      card.addEventListener("click", () => openAsset(asset, card));
      return card;
    }),
  );
  setStatus("media-count", `${total} ${t("photosInLibrary")}`);
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  setStatus("media-page", `${t("page")} ${page} / ${pages}`);
  byId<HTMLButtonElement>("media-prev").disabled = page <= 1;
  byId<HTMLButtonElement>("media-next").disabled = page >= pages;
}

const dialog = byId<HTMLDialogElement>("asset-dialog");
const assetForm = byId<HTMLFormElement>("asset-form");
const linkForm = byId<HTMLFormElement>("link-form");
const select = byId<HTMLSelectElement>("perfume-select");
async function searchPerfumes() {
  const params = new URLSearchParams({ page_size: "24" });
  const text = byId<HTMLInputElement>("perfume-search").value.trim();
  if (text) params.set("q", text);
  try {
    const result = await api<Product[]>("/api/v1/admin/products?" + params);
    select.replaceChildren(
      ...result.data.map((product) =>
        el(
          "option",
          `${product.brand.name} · ${product.name} (${product.images.length}/5)`,
          { value: product.id },
        ),
      ),
    );
  } catch (error) {
    show(error);
  }
}
function openAsset(asset: MediaAsset, opener: HTMLElement) {
  selected = asset;
  deleteArmed = undefined;
  byId("asset-delete").textContent = t("deletePhoto");
  const image = byId<HTMLImageElement>("asset-image");
  image.src = asset.url;
  image.alt = asset.name;
  (assetForm.elements.namedItem("name") as HTMLInputElement).value = asset.name;
  setStatus("asset-status", "");
  assetForm
    .querySelectorAll<HTMLElement>("[data-form-error]")
    .forEach((node) => (node.hidden = true));
  linkForm
    .querySelectorAll<HTMLElement>("[data-form-error]")
    .forEach((node) => (node.hidden = true));
  openDialog(dialog, opener);
  void searchPerfumes();
}

let searchTimer: number | undefined;
byId("media-search").addEventListener("input", (event) => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => {
    query = (event.target as HTMLInputElement).value.trim();
    page = 1;
    void load();
  }, 300);
});
byId("media-prev").addEventListener("click", () => {
  page = Math.max(1, page - 1);
  void load();
});
byId("media-next").addEventListener("click", () => {
  page += 1;
  void load();
});
let perfumeTimer: number | undefined;
byId("perfume-search").addEventListener("input", () => {
  window.clearTimeout(perfumeTimer);
  perfumeTimer = window.setTimeout(searchPerfumes, 300);
});
byId<HTMLInputElement>("media-upload").addEventListener(
  "change",
  async (event) => {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    const data = new FormData();
    data.set("file", file);
    data.set("name", file.name.replace(/\.[^.]+$/, "").slice(0, 250));
    try {
      await api("/api/v1/admin/media", { method: "POST", body: data });
      page = 1;
      query = "";
      byId<HTMLInputElement>("media-search").value = "";
      await load();
      setStatus("media-count", t("photoUploaded"));
    } catch (error) {
      show(error);
    } finally {
      input.value = "";
    }
  },
);

bindDialogs();
bindForm(
  assetForm,
  async (values) => {
    if (!selected) return;
    const result = await api<MediaAsset>(
      "/api/v1/admin/media/" + selected.id,
      jsonRequest("PATCH", {
        version: selected.version,
        name: String(values.get("name") ?? "").trim(),
      }),
    );
    selected = result.data;
    setStatus("asset-status", t("saved"));
    await load();
  },
  locale,
);
byId("asset-delete").addEventListener("click", async (event) => {
  if (!selected) return;
  const button = event.currentTarget as HTMLButtonElement;
  if (deleteArmed === undefined) {
    button.textContent = t("confirmDelete");
    deleteArmed = window.setTimeout(() => {
      deleteArmed = undefined;
      button.textContent = t("deletePhoto");
    }, 6000);
    return;
  }
  window.clearTimeout(deleteArmed);
  deleteArmed = undefined;
  button.textContent = t("deletePhoto");
  try {
    await api(
      "/api/v1/admin/media/" + selected.id,
      jsonRequest("DELETE", { version: selected.version }),
    );
    dialog.close();
    await load();
  } catch (error) {
    setStatus("asset-status", errorMessage(error, locale));
  }
});
bindForm(
  linkForm,
  async () => {
    if (!selected || !select.value) return;
    try {
      await api(
        "/api/v1/admin/products/" + select.value + "/images",
        jsonRequest("POST", { asset_id: selected.id }),
      );
      setStatus("asset-status", t("photoLinked"));
      await searchPerfumes();
    } catch (error) {
      if (error instanceof ApiError && error.body.code === "DATA_CONFLICT")
        setStatus("asset-status", t("alreadyLinked"));
      else throw error;
    }
  },
  locale,
);
void load();
