import { showError } from "./errors";
import type { Locale } from "../i18n";
const pending = new WeakSet<HTMLFormElement>();
export function bindForm(
  form: HTMLFormElement,
  action: (values: FormData) => Promise<void>,
  locale: Locale,
) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (pending.has(form) || !form.reportValidity()) return;
    const active = document.activeElement as HTMLElement | null;
    const values = new FormData(form),
      error = form.querySelector<HTMLElement>("[data-form-error]");
    pending.add(form);
    form.setAttribute("aria-busy", "true");
    form.inert = true;
    if (error) error.hidden = true;
    try {
      await action(values);
    } catch (err) {
      form.inert = false;
      if (error) showError(error, err, locale);
    } finally {
      pending.delete(form);
      form.inert = false;
      form.removeAttribute("aria-busy");
      if (active && active !== document.activeElement && form.contains(active))
        active.focus();
    }
  });
}
