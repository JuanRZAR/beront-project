import { api, jsonRequest } from "../../shared/http/client";
import { bindForm } from "../../shared/http/forms";
import { ApiError } from "../../shared/http/errors";
import { translate, number, type Locale } from "../../shared/i18n";
import { decimalUnits, decimalString } from "./decimal";
import type { Movement } from "../../shared/http/contracts";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const dialog = document.querySelector<HTMLDialogElement>("#stock-dialog");
const form = document.querySelector<HTMLFormElement>("#stock-form");
let selected: {
  id: string;
  kind: string;
  amount: string;
  version: number;
} | null = null;
let operation: { signature: string; id: string } | null = null;
if (dialog && form) {
  const delta = document.querySelector<HTMLInputElement>("#stock-delta")!;
  function preview() {
    if (!selected) return false;
    const current = decimalUnits(selected.amount)!,
      difference = decimalUnits(delta.value),
      unit = selected.kind === "decant" ? "ml" : t("units");
    const invalid =
      !!delta.value &&
      (difference === null ||
        difference === 0n ||
        current + difference < 0n ||
        (selected.kind === "full_bottle" && difference % 100n !== 0n));
    document.getElementById("stock-preview-error")!.hidden = !invalid;
    document.getElementById("new-balance")!.textContent = invalid
      ? "—"
      : number(decimalString(current + (difference ?? 0n))) + " " + unit;
    return !invalid && difference !== null && difference !== 0n;
  }
  document
    .querySelectorAll<HTMLButtonElement>("[data-adjust-stock]")
    .forEach((button) =>
      button.addEventListener("click", () => {
        selected = {
          id: button.dataset.target!,
          kind: button.dataset.kind!,
          amount: button.dataset.amount!,
          version: Number(button.dataset.version),
        };
        operation = null;
        form.reset();
        delta.step = selected.kind === "decant" ? ".01" : "1";
        form.querySelector<HTMLElement>("[data-form-error]")!.hidden = true;
        document.getElementById("stock-product-name")!.textContent =
          button.dataset.name!;
        document.getElementById("current-balance")!.textContent =
          number(selected.amount) +
          " " +
          (selected.kind === "decant" ? "ml" : t("units"));
        preview();
        dialog.showModal();
      }),
    );
  for (const id of ["close-stock-dialog", "cancel-stock"])
    document
      .getElementById(id)!
      .addEventListener("click", () => dialog.close());
  delta.addEventListener("input", preview);
  bindForm(
    form,
    async (values) => {
      if (!selected || !preview())
        throw new ApiError(422, {
          code: "INVALID_ADJUSTMENT",
          message: "",
          details: [],
        });
      const payload = {
        kind: selected.kind,
        target_id: selected.id,
        version: selected.version,
        delta: values.get("delta"),
        reason: values.get("reason"),
      };
      const signature = JSON.stringify(payload);
      if (!operation || operation.signature !== signature)
        operation = { signature, id: crypto.randomUUID() };
      await api<Movement>(
        "/api/v1/admin/inventory/adjustments",
        jsonRequest("POST", { ...payload, operation_id: operation.id }),
      );
      dialog.close();
      const url = new URL(location.href);
      url.searchParams.set("updated", "1");
      location.replace(url.pathname + url.search);
    },
    locale,
  );
}
document
  .querySelector(".inventory-tabs")
  ?.addEventListener("keydown", (event) => {
    const key = event as KeyboardEvent;
    if (!["ArrowLeft", "ArrowRight"].includes(key.key)) return;
    key.preventDefault();
    const tabs = [
        ...document.querySelectorAll<HTMLAnchorElement>(
          '.inventory-tabs [role="tab"]',
        ),
      ],
      index = tabs.indexOf(document.activeElement as HTMLAnchorElement);
    const next =
      tabs[
        (index + (key.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length
      ];
    next?.focus();
    next?.click();
  });
