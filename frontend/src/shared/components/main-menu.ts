import { api } from "../http/client";
import { ApiError } from "../http/errors";
import type { Session } from "../http/contracts";
import { translate } from "../i18n";
import "../../features/identity/logout";
import "../../features/cart/header";

const t = translate(document.documentElement.lang === "en" ? "en" : "es");
const launcher = document.querySelector<HTMLButtonElement>("#main-menu-toggle");
const dialog = document.querySelector<HTMLDialogElement>("#main-menu-dialog");
if (launcher && dialog) {
  const guest = dialog.querySelector<HTMLElement>("[data-menu-guest]");
  const logout = dialog.querySelector<HTMLElement>("[data-logout]");
  const status = dialog.querySelector<HTMLElement>("#main-menu-session");
  const protectedLinks = dialog.querySelectorAll<HTMLElement>(
    "[data-menu-permission]",
  );
  let restoreFocus = true;
  let requestId = 0;

  async function refreshSession() {
    if (!guest || !logout || !status) return;
    const request = ++requestId;
    protectedLinks.forEach((link) => (link.hidden = true));
    guest.hidden = true;
    logout.hidden = true;
    status.textContent = t("loading");
    try {
      const { data } = await api<Session>("/api/v1/auth/session");
      if (request !== requestId) return;
      const admin = data.role === "admin";
      protectedLinks.forEach((link) => {
        link.hidden =
          !admin || !data.permissions.includes(link.dataset.menuPermission!);
      });
      logout.hidden = !admin;
      guest.hidden = admin;
      status.textContent = "";
    } catch (error) {
      if (request !== requestId) return;
      guest.hidden = false;
      status.textContent =
        error instanceof ApiError && error.status === 401 ? "" : t("loadError");
    }
  }
  function close(focus = true) {
    restoreFocus = focus;
    dialog!.close();
  }
  launcher.addEventListener("click", () => {
    restoreFocus = true;
    dialog.showModal();
    launcher.setAttribute("aria-expanded", "true");
    (
      dialog.querySelector<HTMLElement>(
        '[aria-current="page"]:not([data-menu-permission])',
      ) ?? dialog.querySelector<HTMLElement>(".main-menu-tile")
    )?.focus();
    void refreshSession();
  });
  dialog.addEventListener("close", () => {
    launcher.setAttribute("aria-expanded", "false");
    if (restoreFocus) launcher.focus({ preventScroll: true });
  });
  dialog.addEventListener("click", async (event) => {
    const target = event.target as HTMLElement;
    if (target === dialog || target.closest("[data-menu-close]")) close();
    if (
      target.closest("[data-menu-cart]") &&
      document.getElementById("cart-dialog")
    ) {
      event.preventDefault();
      event.stopPropagation();
      close(false);
      await import("../../features/cart/dialog");
      window.dispatchEvent(
        new CustomEvent("beront:open-cart", { detail: launcher }),
      );
    }
    if (target.closest("[data-menu-accessibility]")) {
      const panel = document.getElementById("a11y-panel");
      if (!panel) return;
      close(false);
      panel.showPopover();
      panel.querySelector<HTMLElement>("button, input")?.focus();
      const restore = () => {
        if (panel.matches(":popover-open")) return;
        launcher.focus({ preventScroll: true });
        panel.removeEventListener("toggle", restore);
      };
      panel.addEventListener("toggle", restore);
    }
  });
  dialog.addEventListener("keydown", (event) => {
    if (event.key === "Tab") {
      const controls = [
        ...dialog.querySelectorAll<HTMLElement>(
          "a[href], button:not(:disabled)",
        ),
      ].filter((node) => node.checkVisibility());
      const first = controls[0];
      const last = controls.at(-1);
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
      return;
    }
    if (
      !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)
    )
      return;
    const active = document.activeElement;
    if (!(active instanceof HTMLElement) || !dialog.contains(active)) return;
    const bounds = active.getBoundingClientRect();
    const origin = {
      x: bounds.x + bounds.width / 2,
      y: bounds.y + bounds.height / 2,
    };
    const horizontal = event.key === "ArrowLeft" || event.key === "ArrowRight";
    const direction =
      event.key === "ArrowLeft" || event.key === "ArrowUp" ? -1 : 1;
    const candidates = [
      ...dialog.querySelectorAll<HTMLElement>("a[href], button:not(:disabled)"),
    ]
      .filter((node) => node !== active && node.checkVisibility())
      .map((node) => {
        const rect = node.getBoundingClientRect();
        const dx = rect.x + rect.width / 2 - origin.x;
        const dy = rect.y + rect.height / 2 - origin.y;
        return {
          node,
          forward: (horizontal ? dx : dy) * direction,
          cross: Math.abs(horizontal ? dy : dx),
        };
      })
      .filter(({ forward, cross }) => forward > 1 && cross < forward)
      .sort((a, b) => a.forward + a.cross * 2 - (b.forward + b.cross * 2));
    event.preventDefault();
    candidates[0]?.node.focus();
  });
}
