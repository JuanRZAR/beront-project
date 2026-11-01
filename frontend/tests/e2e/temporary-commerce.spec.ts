import { test, expect } from "@playwright/test";
import { resolve } from "node:path";

const views = [
  "checkout",
  "order-tracking",
  "admin-settings",
  "admin-media",
  "admin-orders",
];

test("las cinco vistas responden en móvil y escritorio, ES/EN, sin ventas ni desbordamientos", async ({
  page,
}) => {
  const errors: string[] = [],
    writes: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.method() === "POST") writes.push(request.url());
  });
  for (const width of [320, 360, 390, 768, 1024, 1440])
    for (const view of views) {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto("/temporal/" + view + ".html");
      await expect(page.locator("h1")).toBeVisible();
      if (view === "admin-media")
        await expect(page.locator("#media-count")).toContainText("132");
      else if (view !== "admin-settings")
        await expect(page.locator("[data-product-line] strong")).toHaveCount(1);
      else await expect(page.locator("#list-categories li")).toHaveCount(3);
      await page.evaluate(() => document.fonts.ready);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      if (
        test.info().project.name === "chromium" &&
        [390, 1440].includes(width)
      )
        await page.screenshot({
          path: resolve(
            "../design/reviews/commerce-" + view + "-" + width + ".png",
          ),
          fullPage: view !== "admin-media",
        });
      await page.locator("[data-lang=en]").click();
      await expect(page.locator("html")).toHaveAttribute("lang", "en");
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
    }
  expect(errors).toEqual([]);
  expect(writes).toEqual([]);
});

test("pago, términos y recuperación usan controles accesibles sin enviar datos", async ({
  page,
}) => {
  await page.goto("/temporal/checkout.html");
  const pay = page.locator("#pay-button");
  await expect(pay).toBeDisabled();
  await page.locator("input[value=bank_transfer]").check();
  await expect(page.locator("#bank-panel")).toBeVisible();
  await expect(page.locator("#receipt")).toHaveAttribute("required", "");
  await page.locator("input[value=whatsapp]").check();
  await expect(page.locator("#bank-panel")).toBeHidden();
  await page.locator("#accept-terms").check();
  await expect(pay).toBeEnabled();
  await page.locator("[data-open=terms-dialog]").click();
  await expect(page.locator("#terms-dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator("[data-open=terms-dialog]")).toBeFocused();
  await page.goto("/temporal/order-tracking.html");
  await page.locator("[data-open=recovery-dialog]").click();
  await page.locator("#recovery-form input").fill("1712345678");
  await page.locator("#recovery-form button").click();
  await expect(page.locator("#recovery-status")).toContainText(
    "correo registrado",
  );
});

test("la biblioteca lee fotos del backend y conserva foco al elegir hasta cinco", async ({
  page,
}) => {
  await page.goto("/temporal/admin-media.html");
  await expect(page.locator("#media-gallery .media-card")).toHaveCount(132);
  await expect(page.locator("#media-gallery img").first()).toHaveAttribute(
    "src",
    /^\/temporal\/seed\/media\/[a-f0-9]{32}\.webp$/,
  );
  await page.locator("[data-open=product-images-dialog]").click();
  await page.locator("#open-picker").click();
  const cards = page.locator("#picker-gallery .media-card");
  await cards.first().focus();
  await page.keyboard.press("Space");
  await expect(cards.first()).toBeFocused();
  for (let index = 1; index < 6; index++) await cards.nth(index).click();
  await expect(page.locator("#picker-gallery [aria-pressed=true]")).toHaveCount(
    5,
  );
  await expect(page.locator("#selection-status")).toContainText("cinco");
  await page.locator("#use-images").click();
  await expect(page.locator("#image-picker")).toBeHidden();
  await expect(page.locator("#product-image-preview img")).toHaveCount(5);
});

test("configuración y gestión representan las decisiones del propietario", async ({
  page,
}) => {
  await page.goto("/temporal/admin-settings.html");
  await expect(page.locator("#list-categories li")).toHaveCount(3);
  await expect(page.locator("#list-categories")).toContainText("Lattafa");
  await expect(page.locator("#list-audiences li")).toHaveCount(3);
  await expect(page.locator("#list-presentations li")).toHaveCount(10);
  await expect(page.locator("#panel-categories")).not.toContainText("Mujer");
  await page.locator("#tab-categories").focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("#panel-audiences")).toBeVisible();
  await expect(page.locator("#panel-audiences")).toContainText("Mujer");
  await page.locator("#tab-accords").click();
  await expect(page.locator("#list-accords")).toContainText("Aún no hay");
  await page.locator("#form-accords [name=name_es]").fill("Amaderado");
  await page.locator("#form-accords [name=name_en]").fill("Woody");
  await page.locator("#form-accords button").click();
  await expect(page.locator("#list-accords")).toContainText("Amaderado");
  await page.locator("#tab-categories").click();
  await page.locator("#settings-brand").selectOption({ label: "Afnan" });
  await page
    .locator("#settings-brand-category")
    .selectOption({ label: "Nicho" });
  await page.locator("#brand-form button").click();
  await expect(page.locator("#list-categories")).toContainText("Afnan");
  await page.locator("#tab-delivery").click();
  await expect(page.locator("#panel-delivery")).toBeVisible();
  const destination = page.locator("#destination-form");
  await destination.locator("[name=province]").fill("Pichincha");
  await destination.locator("[name=city]").fill("Quito");
  await destination.locator("[name=fee]").fill("6.25");
  await destination.locator("button").click();
  await expect(page.locator("#destination-list")).toContainText("6.25");
  await page.locator("#tab-flow").click();
  await page.locator("#status-form [name=name_es]").fill("Revisión adicional");
  await page.locator("#status-form [name=name_en]").fill("Additional review");
  await page.locator("#status-form button").click();
  await expect(page.locator("#status-list")).toContainText(
    "Revisión adicional",
  );
  await page.goto("/temporal/admin-orders.html");
  await expect(page.locator("#order-status")).not.toBeEmpty();
  await page.locator("#order-scenario").selectOption("conflict");
  await page.locator("#approve-payment").click();
  await expect(page.locator("#admin-status")).toContainText(
    "no se descuenta inventario",
  );
  await page.locator("#order-scenario").selectOption("pending");
  await page.locator("#approve-payment").click();
  await expect(page.locator("#shipping-form")).toBeVisible();
  await page.locator("#shipping-form [name=guide]").fill("Guía de revisión");
  await page
    .locator("#shipping-form [name=tracking]")
    .fill("Seguimiento de revisión");
  await page.locator("#shipping-form button").click();
  await expect(page.locator("#order-status")).toHaveText("Enviado");
});
