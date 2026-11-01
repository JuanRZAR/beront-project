import { test, expect } from "@playwright/test";

const pages = [
  "catalog",
  "product",
  "cart",
  "login",
  "admin-catalog",
  "admin-inventory",
];

for (const width of [320, 360, 390, 768, 1024, 1440]) {
  test(`prototipos accesibles a ${width}px`, async ({ page, browserName }) => {
    await page.setViewportSize({ width, height: 1000 });
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    for (const name of pages) {
      await page.goto(`/prototypes/${name}.html`);
      await page.evaluate(() => document.fonts.ready);
      await expect(page.locator("h1")).toBeVisible();
      const dimensions = await page.evaluate(() => ({
        width: window.innerWidth,
        content: document.documentElement.scrollWidth,
      }));
      expect(dimensions.content, name).toBeLessThanOrEqual(dimensions.width);
      if (browserName === "chromium" && [390, 1440].includes(width)) {
        await page.screenshot({
          path: `../design/reviews/${name}-${width}.png`,
          fullPage: true,
          animations: "disabled",
        });
      }
    }
    expect(errors).toEqual([]);
  });
}

test("filtros, cambio de apartado e idioma", async ({ page }) => {
  await page.goto("/prototypes/catalog.html");
  await expect(page.locator(".product-card")).toHaveCount(3);
  await page.locator('input[name="classification"][value="arabic"]').check();
  await expect(page.locator(".product-card")).toHaveCount(1);
  await page.getByRole("button", { name: "Limpiar", exact: true }).click();
  await page.locator("#catalog-search").fill("sin coincidencias");
  await expect(page.locator(".empty-state")).toBeVisible();
  await page.getByRole("button", { name: "EN", exact: true }).click();
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(
    page.getByRole("link", { name: "Full bottles", exact: true }).last(),
  ).toBeVisible();
});

test("selección y carrito de demostración", async ({ page }) => {
  await page.goto("/prototypes/product.html");
  await page.getByRole("button", { name: "10 ml", exact: true }).click();
  await expect(page.locator("#detail-price")).toContainText("$20.00");
  await page
    .getByRole("button", { name: "Agregar al carrito", exact: true })
    .click();
  await expect(page.locator("#toast")).toBeVisible();
  await page.goto("/prototypes/cart.html");
  await expect(page.locator("#cart-total")).toHaveText("$52.50");
  await page.locator('[data-remove="0"]').click();
  await expect(page.locator("#cart-items tr")).toHaveCount(1);
  await page.getByRole("button", { name: "Continuar por WhatsApp" }).click();
  await expect(page.locator("#toast")).toContainText("Demostración");
});

test("estados vacíos, agotados y de error", async ({ page }) => {
  await page.goto("/prototypes/catalog.html?state=empty");
  await expect(page.locator(".empty-state")).toBeVisible();
  await page.goto("/prototypes/product.html?state=soldout");
  await expect(page.locator("#add-to-cart")).toBeDisabled();
  await page.goto("/prototypes/cart.html?state=soldout");
  await expect(page.locator("#continue-whatsapp")).toBeDisabled();
  await page.goto("/prototypes/login.html?state=error");
  await expect(page.locator("#login-notice")).toContainText("no son válidos");
});

test("botella completa y carrito con ambos tipos", async ({ page }) => {
  await page.goto("/prototypes/catalog.html?kind=full_bottle");
  await page.locator(".product-card .product-image").first().click();
  await expect(page).toHaveURL(/kind=full_bottle/);
  await expect(page.locator(".sizes button")).toHaveCount(1);
  await expect(page.locator(".sizes button")).toHaveText("100 ml");
  await expect(page.locator("#detail-price")).toContainText("$120.00");
  await page
    .getByRole("button", { name: "Agregar al carrito", exact: true })
    .click();
  await page.goto("/prototypes/cart.html");
  await expect(page.locator("#cart-items tr")).toHaveCount(3);
  await expect(page.locator("#cart-items")).toContainText("Botella completa");
  await expect(page.locator("#cart-total")).toHaveText("$152.50");
});

test("edición y ajuste con validación y diálogo", async ({ page }) => {
  await page.goto("/prototypes/admin-catalog.html");
  await page.locator('[data-edit-product="01"]').click();
  await expect(page.locator("#product-editor")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator("#product-editor")).not.toBeVisible();
  await page.goto("/prototypes/admin-inventory.html");
  await page.locator('[data-adjust="01"]').click();
  await expect(page.locator("#stock-editor")).toBeVisible();
  await page.locator("#stock-delta").fill("-100");
  await expect(page.locator("#adjustment-error")).toBeVisible();
  await page.locator("#stock-delta").fill("-5");
  await expect(page.locator("#new-balance")).toHaveText("40 ml");
  await page.locator("#stock-reason").fill("Movimiento de demostración");
  await page
    .getByRole("button", { name: "Registrar ajuste", exact: true })
    .click();
  await expect(page.locator("#stock-editor")).not.toBeVisible();
  await expect(page.locator("#toast")).toContainText("no se guardaron");
});

test("filtros móviles y cierre por teclado", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/prototypes/catalog.html");
  await page.locator("#open-filters").click();
  await expect(page.locator("#open-filters")).toHaveAttribute(
    "aria-expanded",
    "true",
  );
  await expect(page.locator("#close-filters")).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.locator("#open-filters")).toHaveAttribute(
    "aria-expanded",
    "false",
  );
  await expect(page.locator("#open-filters")).toBeFocused();
});
