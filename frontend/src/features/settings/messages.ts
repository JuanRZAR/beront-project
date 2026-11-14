import { api, jsonRequest } from "../../shared/http/client";
import { bindForm } from "../../shared/http/forms";
import { byId, el } from "../../shared/components/dom";
import { errorMessage } from "../../shared/http/errors";
import { translate, type Locale } from "../../shared/i18n";
import type {
  FeaturedMessage,
  FeaturedText,
  MediaAsset,
} from "../../shared/http/contracts";

const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const path = "/api/v1/admin/home/messages";
const form = byId<HTMLFormElement>("home-message-form");
const field = (name: string) =>
  form.elements.namedItem(name) as HTMLInputElement;
let rows: FeaturedMessage[] = [],
  current: FeaturedMessage | null = null,
  assets: MediaAsset[] = [],
  page = 1,
  total = 0,
  epoch = 0;
const selected = new Map<string, Pick<MediaAsset, "id" | "url" | "name">>();
const textFields = [
  "eyebrow",
  "title",
  "emphasis",
  "body",
  "primary_label",
  "secondary_label",
] as const;
const status = (message: string) => {
  byId("home-message-status").textContent = message;
};
function failure(cause: unknown) {
  const node = byId("settings-error");
  node.textContent = errorMessage(cause, locale);
  node.hidden = false;
}
const localDate = (value: string | null) => {
  if (!value) return "";
  const date = new Date(value),
    pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};
function edit(row: FeaturedMessage | null) {
  current = row;
  form.reset();
  selected.clear();
  status("");
  for (const language of ["es", "en"] as const)
    for (const key of textFields)
      field(`${language}_${key}`).value = row?.content[language][key] ?? "";
  for (const key of [
    "primary_path",
    "secondary_path",
    "icon",
    "stats_kind",
    "position",
  ] as const)
    if (row) field(key).value = String(row[key]);
  field("active").checked = row?.active ?? false;
  field("starts_at").value = localDate(row?.starts_at ?? null);
  field("ends_at").value = localDate(row?.ends_at ?? null);
  row?.images.forEach((asset) => selected.set(asset.id, asset));
  paintImages();
}
function paintRows() {
  byId("home-message-list").replaceChildren(
    ...rows.map((row) => {
      const li = el("li"),
        button = el("button", row.content[locale].title, {
          type: "button",
          class: "text-button",
        });
      button.addEventListener("click", () => {
        edit(row);
        field("es_title").focus();
      });
      li.append(
        button,
        el(
          "small",
          `${row.position} · ${t(row.active ? "active" : "homeDraft")}`,
        ),
      );
      return li;
    }),
  );
}
function paintImages() {
  byId("home-selected-images").replaceChildren(
    ...(selected.size
      ? [...selected.values()].map((asset) => {
          const button = el(
            "button",
            `${t("homeRemoveImage")}: ${asset.name}`,
            { type: "button", class: "text-button" },
          );
          button.addEventListener("click", () => {
            selected.delete(asset.id);
            paintImages();
          });
          return button;
        })
      : [el("p", t("homeNoImages"))]),
  );
  byId("home-media-options").replaceChildren(
    ...assets.map((asset) => {
      const chosen = selected.has(asset.id),
        button = el("button", undefined, {
          type: "button",
          "aria-pressed": String(chosen),
        });
      const photo = el("img", undefined, {
        src: asset.url,
        alt: "",
        loading: "lazy",
        width: "100",
        height: "120",
      });
      button.append(photo, el("span", asset.name));
      (button as HTMLButtonElement).disabled = !chosen && selected.size >= 3;
      button.addEventListener("click", () => {
        if (chosen) selected.delete(asset.id);
        else if (selected.size < 3) selected.set(asset.id, asset);
        else status(t("homeImageLimit"));
        paintImages();
      });
      return button;
    }),
  );
  byId<HTMLButtonElement>("home-library-prev").disabled = page <= 1;
  byId<HTMLButtonElement>("home-library-next").disabled = page * 24 >= total;
  byId("home-library-page").textContent =
    `${page} / ${Math.max(1, Math.ceil(total / 24))}`;
}
async function library(next = 1) {
  const request = ++epoch,
    query = new URLSearchParams({
      page: String(next),
      page_size: "24",
      q: byId<HTMLInputElement>("home-image-search").value,
    });
  try {
    const result = await api<MediaAsset[]>("/api/v1/admin/media?" + query);
    if (request !== epoch) return;
    assets = result.data;
    total = result.meta?.total ?? 0;
    page = next;
    paintImages();
  } catch (cause) {
    failure(cause);
  }
}
export async function loadMessages() {
  rows = (await api<FeaturedMessage[]>(path)).data;
  paintRows();
  edit(rows[0] ?? null);
  if (!rows.length)
    byId("home-message-list").append(el("li", t("homeNoMessages")));
  await library();
}
byId("home-message-new").addEventListener("click", () => {
  edit(null);
  field("es_title").focus();
});
byId("home-library-prev").addEventListener(
  "click",
  () => void library(page - 1),
);
byId("home-library-next").addEventListener(
  "click",
  () => void library(page + 1),
);
let searchTimer = 0;
byId("home-image-search").addEventListener("input", () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => void library(), 300);
});
bindForm(
  form,
  async () => {
    const content = {} as Record<Locale, FeaturedText>;
    for (const language of ["es", "en"] as const)
      content[language] = Object.fromEntries(
        textFields.map((key) => [key, field(`${language}_${key}`).value]),
      ) as unknown as FeaturedText;
    const data = {
      slug: current?.slug ?? "message-" + crypto.randomUUID(),
      content,
      primary_path: field("primary_path").value,
      secondary_path: field("secondary_path").value,
      icon: field("icon").value,
      stats_kind: field("stats_kind").value,
      position: Number(field("position").value),
      active: field("active").checked,
      starts_at: field("starts_at").value
        ? new Date(field("starts_at").value).toISOString()
        : null,
      ends_at: field("ends_at").value
        ? new Date(field("ends_at").value).toISOString()
        : null,
      image_ids: [...selected.keys()],
    };
    const result = await api<FeaturedMessage>(
      current ? path + "/" + current.id : path,
      jsonRequest(
        current ? "PUT" : "POST",
        current ? { ...data, version: current.version } : data,
      ),
    );
    rows = (await api<FeaturedMessage[]>(path)).data;
    paintRows();
    edit(result.data);
    status(t("saved"));
  },
  locale,
);
