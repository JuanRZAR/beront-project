import { api, jsonRequest } from "../../shared/http/client";
import { showError, ApiError } from "../../shared/http/errors";
import { bindForm } from "../../shared/http/forms";
import { mediaUrl } from "../../shared/http/serialization";
import { toast } from "../../shared/components/toast";
import { translate, number, type Locale } from "../../shared/i18n";
import type {
  Product,
  Brand,
  Variant,
  ProductImage,
} from "../../shared/http/contracts";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const raw = document.getElementById("editor-data")?.textContent;
if (raw) {
  const state = JSON.parse(raw) as { product?: Product; brands: Brand[] };
  const productForm = document.querySelector<HTMLFormElement>("#product-form")!;
  const brandSelect = document.querySelector<HTMLSelectElement>("#brand-id")!;
  const checked = (form: HTMLFormElement, name: string) =>
    form.querySelector<HTMLInputElement>('[name="' + name + '"]')?.checked ??
    false;
  const name = document.querySelector<HTMLInputElement>("#edit-name")!,
    slug = document.querySelector<HTMLInputElement>("#product-slug")!;
  let slugDirty = !!state.product;
  slug.addEventListener("input", () => (slugDirty = true));
  name.addEventListener("input", () => {
    if (!slugDirty)
      slug.value = name.value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "");
  });
  bindForm(
    productForm,
    async (values) => {
      const payload: Record<string, unknown> = {
        name: values.get("name"),
        brand_id: values.get("brand_id"),
        slug: values.get("slug"),
        audience: values.get("audience"),
        description_es: values.get("description_es"),
        description_en: values.get("description_en"),
      };
      if (state.product)
        Object.assign(payload, {
          version: state.product.version,
          published: checked(productForm, "published"),
          archived: checked(productForm, "archived"),
          sold_out: checked(productForm, "sold_out"),
        });
      const result = await api<Product>(
        state.product
          ? "/api/v1/admin/products/" + state.product.id
          : "/api/v1/admin/products",
        jsonRequest(state.product ? "PATCH" : "POST", payload),
      );
      if (!state.product)
        location.replace(
          "/" + locale + "/admin/products/" + result.data.id + "?created=1",
        );
      else {
        state.product = result.data;
        toast(t("saved"));
      }
    },
    locale,
  );
  const dialog = document.querySelector<HTMLDialogElement>("#brand-dialog")!,
    brandForm = document.querySelector<HTMLFormElement>("#brand-form")!;
  let editing: Brand | undefined;
  function openBrand(edit = false) {
    editing = edit
      ? state.brands.find((brand) => brand.id === brandSelect.value)
      : undefined;
    if (edit && !editing) return;
    brandForm.reset();
    brandForm.querySelector<HTMLInputElement>('[name="name"]')!.value =
      editing?.name ?? "";
    brandForm.querySelector<HTMLInputElement>('[name="active"]')!.checked =
      editing?.active ?? true;
    const category = brandForm.querySelector<HTMLSelectElement>(
      '[name="category_id"]',
    )!;
    if (editing?.category_id) category.value = editing.category_id;
    document.getElementById("brand-title")!.textContent = t(
      edit ? "edit" : "newHouse",
    );
    brandForm.querySelector<HTMLElement>("[data-form-error]")!.hidden = true;
    dialog.showModal();
  }
  document
    .getElementById("new-brand")!
    .addEventListener("click", () => openBrand());
  document
    .getElementById("edit-brand")!
    .addEventListener("click", () => openBrand(true));
  document
    .querySelectorAll("[data-close-brand]")
    .forEach((el) => el.addEventListener("click", () => dialog.close()));
  bindForm(
    brandForm,
    async (values) => {
      const payload = {
        name: values.get("name"),
        category_id: values.get("category_id"),
        active: checked(brandForm, "active"),
        ...(editing ? { version: editing.version } : {}),
      };
      const result = await api<Brand>(
        "/api/v1/admin/brands" + (editing ? "/" + editing.id : ""),
        jsonRequest(editing ? "PATCH" : "POST", payload),
      );
      state.brands = state.brands
        .filter((brand) => brand.id !== result.data.id)
        .concat(result.data);
      let option = [...brandSelect.options].find(
        (el) => el.value === result.data.id,
      );
      if (!option) {
        option = new Option("", result.data.id);
        brandSelect.append(option);
      }
      option.textContent =
        result.data.name + (!result.data.active ? " · " + t("inactive") : "");
      brandSelect.value = result.data.id;
      dialog.close();
      toast(t("saved"));
    },
    locale,
  );
  function bindVariant(form: HTMLFormElement) {
    bindForm(
      form,
      async (values) => {
        const result = await api<Variant>(
          "/api/v1/admin/variants/" + form.dataset.variantId,
          jsonRequest("PATCH", {
            version: Number(form.dataset.version),
            price: values.get("price"),
            active: checked(form, "active"),
            sold_out: checked(form, "sold_out"),
          }),
        );
        form.dataset.version = String(result.data.version);
        toast(t("saved"));
      },
      locale,
    );
  }
  document
    .querySelectorAll<HTMLFormElement>(".variant-form[data-variant-id]")
    .forEach(bindVariant);
  const createVariant = document.querySelector<HTMLFormElement>(
    "#variant-create-form",
  );
  if (createVariant)
    bindForm(
      createVariant,
      async (values) => {
        const result = await api<Variant>(
          "/api/v1/admin/products/" + state.product!.id + "/variants",
          jsonRequest("POST", {
            kind: values.get("kind"),
            volume_ml: values.get("volume_ml"),
            price: values.get("price"),
          }),
        );
        const fragment = document
          .querySelector<HTMLTemplateElement>("#variant-template")!
          .content.cloneNode(true) as DocumentFragment;
        const form = fragment.querySelector("form")!;
        form.dataset.variantId = result.data.id;
        form.dataset.version = String(result.data.version);
        form.querySelector("[data-variant-name]")!.textContent =
          t(result.data.kind === "decant" ? "decant" : "fullBottle") +
          " · " +
          number(result.data.volume_ml) +
          " ml";
        form.querySelector<HTMLInputElement>('[name="price"]')!.value =
          result.data.price;
        form.querySelector<HTMLInputElement>('[name="active"]')!.checked =
          !!result.data.active;
        document.getElementById("variant-list")!.append(fragment);
        bindVariant(form);
        createVariant.reset();
        toast(t("variantCreated"));
      },
      locale,
    );
  function bindImage(form: HTMLFormElement) {
    bindForm(
      form,
      async (values) => {
        const result = await api<ProductImage>(
          "/api/v1/admin/images/" + form.dataset.imageId,
          jsonRequest("PATCH", {
            version: Number(form.dataset.version),
            alt_es: values.get("alt_es"),
            alt_en: values.get("alt_en"),
            position: Number(values.get("position")),
          }),
        );
        form.dataset.version = String(result.data.version);
        toast(t("saved"));
      },
      locale,
    );
    form
      .querySelector<HTMLButtonElement>("[data-delete-image]")!
      .addEventListener("click", async (event) => {
        const button = event.currentTarget as HTMLButtonElement;
        button.disabled = true;
        try {
          await api(
            "/api/v1/admin/images/" + form.dataset.imageId,
            jsonRequest("DELETE", { version: Number(form.dataset.version) }),
          );
          form.remove();
          toast(t("saved"));
        } catch (error) {
          showError(
            form.querySelector<HTMLElement>("[data-form-error]")!,
            error,
            locale,
          );
        } finally {
          button.disabled = false;
        }
      });
  }
  document
    .querySelectorAll<HTMLFormElement>(".image-form[data-image-id]")
    .forEach(bindImage);
  const upload = document.querySelector<HTMLFormElement>("#image-upload-form");
  if (upload)
    bindForm(
      upload,
      async (values) => {
        const file = values.get("file");
        if (!(file instanceof File) || file.size > 5 * 1024 * 1024)
          throw new ApiError(413, {
            code: "IMAGE_TOO_LARGE",
            message: "",
            details: [],
          });
        const result = await api<ProductImage>(
          "/api/v1/admin/products/" + state.product!.id + "/images",
          { method: "POST", body: values },
        );
        const fragment = document
          .querySelector<HTMLTemplateElement>("#image-template")!
          .content.cloneNode(true) as DocumentFragment;
        const form = fragment.querySelector("form")!;
        form.dataset.imageId = result.data.id;
        form.dataset.version = String(result.data.version);
        form.querySelector<HTMLImageElement>("img")!.src = mediaUrl(
          result.data.url,
        );
        form.querySelector<HTMLImageElement>("img")!.alt = result.data.alt_es;
        for (const key of ["alt_es", "alt_en", "position"] as const)
          form.querySelector<HTMLInputElement>('[name="' + key + '"]')!.value =
            String(result.data[key]);
        document.getElementById("image-list")!.append(fragment);
        bindImage(form);
        upload.reset();
        toast(t("saved"));
      },
      locale,
    );
}
