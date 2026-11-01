import { api, jsonRequest } from "../../shared/http/client";
import { ApiError, showError } from "../../shared/http/errors";
import type { Locale } from "../../shared/i18n";
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es";
const button = document.querySelector<HTMLButtonElement>("#logout");
button?.addEventListener("click", async () => {
  button.disabled = true;
  try {
    await api("/api/v1/auth/logout", jsonRequest("POST", {}));
    location.replace("/" + locale + "/admin/login");
  } catch (error) {
    if (error instanceof ApiError && error.status === 401)
      location.replace("/" + locale + "/admin/login");
    else
      showError(document.getElementById("admin-global-error")!, error, locale);
  } finally {
    button.disabled = false;
  }
});
