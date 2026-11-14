import { test, expect } from "@playwright/test";

test("menú central: teclado, accesibilidad y adaptación por dispositivo", async ({
  page,
}) => {
  test.setTimeout(90000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/es/");
  const toggle = page.locator("#main-menu-toggle");
  const menu = page.getByRole("dialog", {
    name: "Menú principal",
    exact: true,
  });
  for (const width of [
    320, 360, 390, 412, 600, 768, 820, 840, 1024, 1200, 1280, 1440, 1600, 1920,
  ]) {
    await page.setViewportSize({ width, height: 900 });
    const box = await toggle.boundingBox();
    expect(Math.abs(box!.x + box!.width / 2 - width / 2)).toBeLessThan(2);
    await toggle.click();
    await expect(menu).toBeVisible();
    await expect(
      menu.getByRole("link", { name: "Acceso administrativo" }),
    ).toBeVisible();
    await expect(menu.locator("[data-menu-permission]:visible")).toHaveCount(0);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(width);
    expect(
      await menu
        .locator(".main-menu-panel")
        .evaluate((panel) => panel.scrollWidth <= panel.clientWidth),
    ).toBe(true);
    const focused = await page.evaluate(
      () => document.activeElement?.textContent,
    );
    await page.keyboard.press("ArrowRight");
    expect(
      await page.evaluate(() => document.activeElement?.textContent),
    ).not.toBe(focused);
    await page.keyboard.press("Escape");
    await expect(toggle).toBeFocused();
  }
  await toggle.click();
  await menu
    .getByRole("button", { name: "Accesibilidad", exact: true })
    .click();
  await expect(menu).not.toBeVisible();
  const accessibility = page.locator("#a11y-panel");
  await expect(accessibility).toBeVisible();
  await accessibility
    .getByRole("button", { name: "Muy grande", exact: true })
    .click();
  await accessibility.getByLabel("Alto contraste", { exact: true }).check();
  await page.keyboard.press("Escape");
  await expect(toggle).toBeFocused();
  for (const width of [320, 600, 840, 1200, 1600, 1920]) {
    await page.setViewportSize({ width, height: 500 });
    await toggle.click();
    expect(
      await menu
        .locator(".main-menu-panel")
        .evaluate((panel) => panel.scrollWidth <= panel.clientWidth),
    ).toBe(true);
    const access = menu.getByRole("link", { name: "Acceso administrativo" });
    await expect(access).toBeVisible();
    await access.focus();
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    expect(
      await menu.evaluate((node) => node.contains(document.activeElement)),
    ).toBe(true);
    await page.keyboard.press("Escape");
  }
});

test("el menú abre el carrito y conserva la ruta al cambiar de idioma", async ({
  page,
}) => {
  await page.goto("/es/catalog/decants?q=Perfume");
  const toggle = page.locator("#main-menu-toggle");
  const menu = page.locator("#main-menu-dialog");
  await toggle.click();
  await menu.locator("[data-menu-cart]").click();
  await expect(menu).not.toBeVisible();
  await expect(page.locator("#cart-dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(toggle).toBeFocused();
  await toggle.click();
  await menu.getByRole("link", { name: "Idioma English" }).click();
  await expect(page).toHaveURL(/\/en\/catalog\/decants\?q=Perfume/);
  await page.locator("#main-menu-toggle").click();
  await expect(
    page.getByRole("dialog", { name: "Main menu", exact: true }),
  ).toBeVisible();
  await menu.getByRole("link", { name: "Full bottles", exact: true }).click();
  await expect(page).toHaveURL(/\/en\/catalog\/full-bottles/);
});

test("los accesos administrativos siguen la sesión real y el cierre la revoca", async ({
  page,
}) => {
  await page.goto("/es/admin/login");
  await page
    .locator('[name="username"]')
    .fill(process.env.BERONT_E2E_USERNAME!);
  await page
    .locator('[name="password"]')
    .fill(process.env.BERONT_E2E_PASSWORD!);
  await page.getByRole("button", { name: "Ingresar", exact: true }).click();
  await expect(page).toHaveURL(/\/admin\/products/);
  await page.locator("#main-menu-toggle").click();
  const menu = page.locator("#main-menu-dialog");
  await expect(
    menu.getByRole("link", { name: "Inventario", exact: true }),
  ).toBeVisible();
  await expect(menu.locator("[data-menu-guest]")).not.toBeVisible();
  await menu.getByRole("link", { name: "Inicio", exact: true }).click();
  await page.locator("#main-menu-toggle").click();
  await expect(
    menu.getByRole("link", { name: "Inventario", exact: true }),
  ).toBeVisible();
  await menu.getByRole("button", { name: "Salir", exact: true }).click();
  await expect(page).toHaveURL(/\/admin\/login/);
  expect((await page.request.get("/api/v1/auth/session")).status()).toBe(401);
  await page.locator("#main-menu-toggle").click();
  await expect(menu.locator("[data-menu-guest]")).toBeVisible();
  await expect(menu.locator("[data-menu-permission]:visible")).toHaveCount(0);
});

test("un fallo de sesión mantiene ocultos los controles privados", async ({
  page,
}) => {
  await page.route("**/api/v1/auth/session", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: { code: "SERVICE_UNAVAILABLE", details: [] },
      }),
    }),
  );
  await page.goto("/es/");
  await page.locator("#main-menu-toggle").click();
  const menu = page.locator("#main-menu-dialog");
  await expect(menu.locator("#main-menu-session")).not.toHaveText("Cargando…");
  await expect(menu.locator("[data-menu-guest]")).toBeVisible();
  await expect(menu.locator("[data-menu-permission]:visible")).toHaveCount(0);
  await expect(menu.locator("[data-logout]")).not.toBeVisible();
});
