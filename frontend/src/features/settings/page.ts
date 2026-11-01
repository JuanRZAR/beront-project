import { api, jsonRequest } from "../../shared/http/client";
import { bindForm } from "../../shared/http/forms";
import { errorMessage } from "../../shared/http/errors";
import { translate, type Locale } from "../../shared/i18n";
import { byId, el, setStatus, slugify } from "../../shared/components/dom";
import type {
  AdminBrand,
  Bank,
  City,
  OptionRow,
  OrderStatus,
  OrderTransitionRow,
  Province,
  StoreSettings,
} from "../../shared/http/contracts";

const locale: Locale = document.documentElement.lang === "en" ? "en" : "es";
const t = translate(locale);
const label = (row: { name_es: string; name_en: string }) =>
  locale === "en" ? row.name_en : row.name_es;
const OPTIONS = [
  "categories",
  "audiences",
  "accords",
  "usages",
  "profiles",
] as const;
const catalogPath = (resource: string) =>
  "/api/v1/admin/catalog-options/" + resource;
const rows: Record<string, OptionRow[]> = {};
let brands: AdminBrand[] = [];
let provinces: Province[] = [];
let cities: City[] = [];
let banks: Bank[] = [];
let storeSettings: StoreSettings | null = null;
let statuses: (OrderStatus & { id: string; version: number })[] = [];
let transitions: OrderTransitionRow[] = [];
const loaded = new Set<string>();

function flash(text: string) {
  setStatus("settings-status", text);
}
function failure(error: unknown) {
  const node = byId("settings-error");
  node.textContent = errorMessage(error, locale);
  node.hidden = false;
}
async function fetchList<T>(path: string) {
  return (await api<T[]>(path)).data;
}
function item(title: string, detail?: string) {
  const li = el("li");
  const text = el("div");
  text.append(el("strong", title));
  if (detail) text.append(el("small", detail));
  li.append(text);
  return li;
}
function emptyRow() {
  return item(t("noOptions"));
}
function editButton(fill: () => void) {
  const button = el("button", t("edit"), {
    type: "button",
    class: "text-button",
  });
  button.addEventListener("click", fill);
  return button;
}

function renderOptions(resource: (typeof OPTIONS)[number]) {
  const list = byId("list-" + resource);
  const items = rows[resource] ?? [];
  list.replaceChildren(
    ...(items.length
      ? items.map((row) => {
          const names =
            resource === "categories"
              ? brands
                  .filter((brand) => brand.category_id === row.id)
                  .map((brand) => brand.name)
              : [];
          const li = item(
            label(row),
            resource === "categories"
              ? `${names.length} ${t("houses")}: ${names.join(", ")}`
              : undefined,
          );
          li.append(
            editButton(() => {
              const form = byId<HTMLFormElement>("form-" + resource);
              form.dataset.edit = row.id;
              (form.elements.namedItem("name_es") as HTMLInputElement).value =
                row.name_es;
              (form.elements.namedItem("name_en") as HTMLInputElement).value =
                row.name_en;
              (form.elements.namedItem("name_es") as HTMLInputElement).focus();
            }),
          );
          return li;
        })
      : [emptyRow()]),
  );
  if (resource === "categories") renderBrands();
}
function renderBrands() {
  const select = byId<HTMLSelectElement>("settings-brand");
  const current = select.value;
  select.replaceChildren(
    ...brands.map((brand) => el("option", brand.name, { value: brand.id })),
  );
  if (current) select.value = current;
  const category = byId<HTMLSelectElement>("settings-brand-category");
  category.replaceChildren(
    ...(rows.categories ?? []).map((row) =>
      el("option", label(row), { value: row.id }),
    ),
  );
  const sync = () => {
    category.value =
      brands.find((brand) => brand.id === select.value)?.category_id ?? "";
  };
  select.onchange = sync;
  sync();
}
function renderPresentations() {
  byId("list-presentations").replaceChildren(
    ...(rows.presentations ?? []).map((row) =>
      item(
        label(row),
        `${row.kind === "decant" ? "Decant" : t("fullBottle")} · ${Number(row.volume_ml)} ml`,
      ),
    ),
  );
}
function renderDelivery() {
  byId("province-options").replaceChildren(
    ...provinces.map((row) => el("option", row.name, { value: row.name })),
  );
  const list = byId("list-cities");
  list.replaceChildren(
    ...(cities.length
      ? cities.map((city) => {
          const province = provinces.find((row) => row.id === city.province_id);
          const li = item(
            city.name,
            `${province?.name ?? ""} · USD ${city.shipping_fee}`,
          );
          li.append(
            editButton(() => {
              const form = byId<HTMLFormElement>("destination-form");
              (form.elements.namedItem("province") as HTMLInputElement).value =
                province?.name ?? "";
              (form.elements.namedItem("city") as HTMLInputElement).value =
                city.name;
              (form.elements.namedItem("fee") as HTMLInputElement).value =
                city.shipping_fee;
              byId("province-code-field").hidden = true;
              (form.elements.namedItem("fee") as HTMLInputElement).focus();
            }),
          );
          return li;
        })
      : [emptyRow()]),
  );
}
function renderBanks() {
  byId("list-banks").replaceChildren(
    ...banks.map((bank) =>
      item(bank.bank_name, `${bank.account_type} · ${bank.account_number}`),
    ),
  );
}
function renderContact() {
  const form = byId<HTMLFormElement>("contact-form");
  (form.elements.namedItem("whatsapp_number") as HTMLInputElement).value =
    storeSettings?.whatsapp_number ?? "";
  (form.elements.namedItem("terms_es") as HTMLTextAreaElement).value =
    storeSettings?.terms_es ?? "";
  (form.elements.namedItem("terms_en") as HTMLTextAreaElement).value =
    storeSettings?.terms_en ?? "";
}
function renderFlow() {
  const list = byId("list-statuses");
  list.replaceChildren(
    ...statuses.map((row) => {
      const li = item(
        label(row),
        row.purpose ? t("entryStatus") : t("workflowStatus"),
      );
      li.append(
        editButton(() => {
          const form = byId<HTMLFormElement>("status-form");
          form.dataset.edit = row.id;
          (form.elements.namedItem("name_es") as HTMLInputElement).value =
            row.name_es;
          (form.elements.namedItem("name_en") as HTMLInputElement).value =
            row.name_en;
          const phase = form.elements.namedItem("phase") as HTMLSelectElement;
          phase.value = row.phase;
          phase.disabled = true;
          (form.elements.namedItem("name_es") as HTMLInputElement).focus();
        }),
      );
      return li;
    }),
  );
  const name = (id: string) => {
    const row = statuses.find((status) => status.id === id);
    return row ? label(row) : "";
  };
  byId("list-transitions").replaceChildren(
    ...(transitions.length
      ? transitions.map((row) =>
          item(
            name(row.from_status_id),
            t("canChangeTo") + " " + name(row.to_status_id),
          ),
        )
      : [emptyRow()]),
  );
  for (const id of ["flow-from", "flow-to"])
    byId(id).replaceChildren(
      ...statuses.map((row) => el("option", label(row), { value: row.id })),
    );
}

const loaders: Record<string, () => Promise<void>> = {
  async categories() {
    [rows.categories, brands] = await Promise.all([
      fetchList<OptionRow>(catalogPath("categories")),
      fetchList<AdminBrand>("/api/v1/admin/brands"),
    ]);
    renderOptions("categories");
  },
  async audiences() {
    rows.audiences = await fetchList<OptionRow>(catalogPath("audiences"));
    renderOptions("audiences");
  },
  async accords() {
    rows.accords = await fetchList<OptionRow>(catalogPath("accords"));
    renderOptions("accords");
  },
  async usages() {
    rows.usages = await fetchList<OptionRow>(catalogPath("usages"));
    renderOptions("usages");
  },
  async profiles() {
    rows.profiles = await fetchList<OptionRow>(catalogPath("profiles"));
    renderOptions("profiles");
  },
  async presentations() {
    rows.presentations = await fetchList<OptionRow>(
      catalogPath("presentations"),
    );
    renderPresentations();
  },
  async delivery() {
    [provinces, cities] = await Promise.all([
      fetchList<Province>("/api/v1/admin/commerce/provinces"),
      fetchList<City>("/api/v1/admin/commerce/cities"),
    ]);
    renderDelivery();
  },
  async banks() {
    [banks, storeSettings] = await Promise.all([
      fetchList<Bank>("/api/v1/admin/commerce/banks"),
      api<StoreSettings | null>("/api/v1/admin/settings").then(
        (result) => result.data,
      ),
    ]);
    renderBanks();
    renderContact();
  },
  async flow() {
    [statuses, transitions] = await Promise.all([
      fetchList<OrderStatus & { id: string; version: number }>(
        "/api/v1/admin/order-flow/statuses",
      ),
      fetchList<OrderTransitionRow>("/api/v1/admin/order-flow/transitions"),
    ]);
    renderFlow();
  },
};
async function reload(key: string) {
  try {
    await loaders[key]?.();
    byId("settings-error").hidden = true;
  } catch (error) {
    failure(error);
  }
}

const tabs = [...document.querySelectorAll<HTMLButtonElement>("[data-tab]")];
function activate(tab: HTMLButtonElement) {
  for (const other of tabs) {
    const selected = other === tab;
    other.setAttribute("aria-selected", String(selected));
    other.tabIndex = selected ? 0 : -1;
    byId("panel-" + other.dataset.tab).hidden = !selected;
  }
  flash("");
  const key = tab.dataset.tab!;
  if (!loaded.has(key)) {
    loaded.add(key);
    void reload(key);
  }
}
for (const tab of tabs) {
  tab.addEventListener("click", () => activate(tab));
  tab.addEventListener("keydown", (event) => {
    const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
    if (!step) return;
    event.preventDefault();
    const next = tabs[(tabs.indexOf(tab) + step + tabs.length) % tabs.length];
    if (!next) return;
    activate(next);
    next.focus();
  });
}

for (const resource of OPTIONS) {
  const form = byId<HTMLFormElement>("form-" + resource);
  bindForm(
    form,
    async (values) => {
      const data = {
        name_es: String(values.get("name_es")).trim(),
        name_en: String(values.get("name_en")).trim(),
      };
      const edit = rows[resource]?.find((row) => row.id === form.dataset.edit);
      if (edit)
        await api(
          catalogPath(resource) + "/" + edit.id,
          jsonRequest("PATCH", { version: edit.version, ...data }),
        );
      else {
        const slug = slugify(data.name_en) || slugify(data.name_es);
        if (!slug || rows[resource]?.some((row) => row.slug === slug)) {
          failure(new Error(slug ? "DUPLICATE_OPTION" : "INVALID_OPTION_NAME"));
          byId("settings-error").textContent = t(
            slug ? "duplicateOption" : "invalidOptionName",
          );
          return;
        }
        await api(
          catalogPath(resource),
          jsonRequest("POST", { slug, ...data }),
        );
      }
      delete form.dataset.edit;
      form.reset();
      byId("settings-error").hidden = true;
      await reload(resource);
      flash(t("saved"));
    },
    locale,
  );
}
bindForm(
  byId<HTMLFormElement>("brand-form"),
  async () => {
    const brand = brands.find(
      (row) => row.id === byId<HTMLSelectElement>("settings-brand").value,
    );
    if (!brand) return;
    await api(
      "/api/v1/admin/brands/" + brand.id,
      jsonRequest("PATCH", {
        version: brand.version,
        category_id: byId<HTMLSelectElement>("settings-brand-category").value,
      }),
    );
    await reload("categories");
    flash(t("saved"));
  },
  locale,
);
const presentationForm = byId<HTMLFormElement>("form-presentations");
bindForm(
  presentationForm,
  async (values) => {
    await api(
      catalogPath("presentations"),
      jsonRequest("POST", {
        kind: values.get("kind"),
        volume_ml: String(values.get("volume_ml")),
        name_es: String(values.get("name_es")).trim(),
        name_en: String(values.get("name_en")).trim(),
      }),
    );
    presentationForm.reset();
    await reload("presentations");
    flash(t("saved"));
  },
  locale,
);

const destination = byId<HTMLFormElement>("destination-form");
const provinceInput = destination.elements.namedItem(
  "province",
) as HTMLInputElement;
provinceInput.addEventListener("input", () => {
  const known = provinces.some(
    (row) =>
      row.name.toLowerCase() === provinceInput.value.trim().toLowerCase(),
  );
  const field = byId("province-code-field");
  field.hidden = known || !provinceInput.value.trim();
  (field.querySelector("input") as HTMLInputElement).required = !field.hidden;
});
bindForm(
  destination,
  async (values) => {
    const name = String(values.get("province")).trim();
    let province = provinces.find(
      (row) => row.name.toLowerCase() === name.toLowerCase(),
    );
    if (!province)
      province = (
        await api<Province>(
          "/api/v1/admin/commerce/provinces",
          jsonRequest("POST", {
            code: String(values.get("province_code")),
            name,
            mainland: true,
          }),
        )
      ).data;
    const cityName = String(values.get("city")).trim();
    const fee = String(values.get("fee"));
    const existing = cities.find(
      (row) =>
        row.province_id === province.id &&
        row.name.toLowerCase() === cityName.toLowerCase(),
    );
    if (existing)
      await api(
        "/api/v1/admin/commerce/cities/" + existing.id,
        jsonRequest("PATCH", { version: existing.version, shipping_fee: fee }),
      );
    else
      await api(
        "/api/v1/admin/commerce/cities",
        jsonRequest("POST", {
          province_id: province.id,
          name: cityName,
          shipping_fee: fee,
        }),
      );
    destination.reset();
    byId("province-code-field").hidden = true;
    await reload("delivery");
    flash(t("saved"));
  },
  locale,
);

const bankForm = byId<HTMLFormElement>("bank-form");
bindForm(
  bankForm,
  async (values) => {
    const data: Record<string, string> = {};
    for (const key of [
      "bank_name",
      "account_type",
      "account_number",
      "holder_name",
      "holder_identification",
    ])
      data[key] = String(values.get(key)).trim();
    await api("/api/v1/admin/commerce/banks", jsonRequest("POST", data));
    bankForm.reset();
    await reload("banks");
    flash(t("saved"));
  },
  locale,
);
bindForm(
  byId<HTMLFormElement>("contact-form"),
  async (values) => {
    await api(
      "/api/v1/admin/settings",
      jsonRequest("PUT", {
        version: storeSettings?.version ?? 0,
        whatsapp_number: String(values.get("whatsapp_number")).trim(),
        terms_es: String(values.get("terms_es")),
        terms_en: String(values.get("terms_en")),
      }),
    );
    await reload("banks");
    flash(t("saved"));
  },
  locale,
);

const statusForm = byId<HTMLFormElement>("status-form");
bindForm(
  statusForm,
  async (values) => {
    const data = {
      name_es: String(values.get("name_es")).trim(),
      name_en: String(values.get("name_en")).trim(),
    };
    const edit = statuses.find((row) => row.id === statusForm.dataset.edit);
    if (edit)
      await api(
        "/api/v1/admin/order-flow/statuses/" + edit.id,
        jsonRequest("PATCH", { version: edit.version, ...data }),
      );
    else {
      const slug = slugify(data.name_en) || slugify(data.name_es);
      if (!slug || statuses.some((row) => row.slug === slug)) {
        failure(new Error("DUPLICATE_OPTION"));
        byId("settings-error").textContent = t(
          slug ? "duplicateOption" : "invalidOptionName",
        );
        return;
      }
      await api(
        "/api/v1/admin/order-flow/statuses",
        jsonRequest("POST", {
          slug,
          ...data,
          phase: String(values.get("phase")),
        }),
      );
    }
    delete statusForm.dataset.edit;
    statusForm.reset();
    (statusForm.elements.namedItem("phase") as HTMLSelectElement).disabled =
      false;
    await reload("flow");
    flash(t("saved"));
  },
  locale,
);
const transitionForm = byId<HTMLFormElement>("transition-form");
bindForm(
  transitionForm,
  async (values) => {
    const from = String(values.get("from")),
      to = String(values.get("to"));
    if (from === to) {
      failure(new Error("SAME_STATUS"));
      byId("settings-error").textContent = t("differentStatuses");
      return;
    }
    if (
      transitions.some(
        (row) => row.from_status_id === from && row.to_status_id === to,
      )
    ) {
      flash(t("saved"));
      return;
    }
    await api(
      "/api/v1/admin/order-flow/transitions",
      jsonRequest("POST", { from_status_id: from, to_status_id: to }),
    );
    await reload("flow");
    flash(t("saved"));
  },
  locale,
);

if (tabs[0]) activate(tabs[0]);
