/// <reference types="astro/client" />
declare namespace App {
  interface Locals {
    locale: import("./shared/i18n").Locale;
    user: import("./shared/http/contracts").Session | null;
  }
}
