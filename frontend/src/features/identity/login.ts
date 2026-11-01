import { api, jsonRequest } from "../../shared/http/client";
import { ApiError, showError } from "../../shared/http/errors";
import { translate, type Locale } from "../../shared/i18n";
import type { Session } from "../../shared/http/contracts";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es",
  t = translate(locale);
const form = document.querySelector<HTMLFormElement>("#login-form")!;
const password = document.querySelector<HTMLInputElement>("#login-password")!;
const toggle = document.querySelector<HTMLButtonElement>("#show-password")!;
const error = document.getElementById("login-error")!;
toggle.addEventListener("click", () => {
  const show = password.type === "password";
  password.type = show ? "text" : "password";
  toggle.setAttribute("aria-pressed", String(show));
  toggle.setAttribute("aria-label", t(show ? "hidePassword" : "showPassword"));
});
let pending = false;
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (pending || !form.reportValidity()) return;
  const values = new FormData(form);
  pending = true;
  form.setAttribute("aria-busy", "true");
  form.querySelector<HTMLButtonElement>('[type="submit"]')!.disabled = true;
  error.hidden = true;
  try {
    await api<Session>(
      "/api/v1/auth/login",
      jsonRequest("POST", {
        username: values.get("username"),
        password: values.get("password"),
      }),
    );
    location.replace("/" + locale + "/admin/products");
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      error.textContent = t("loginError");
      error.hidden = false;
      password.value = "";
      password.focus();
    } else showError(error, err, locale);
  } finally {
    pending = false;
    form.removeAttribute("aria-busy");
    form.querySelector<HTMLButtonElement>('[type="submit"]')!.disabled = false;
  }
});
