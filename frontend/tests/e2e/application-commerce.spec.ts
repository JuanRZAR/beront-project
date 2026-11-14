import { test, expect, type Page } from "@playwright/test";

async function addToCart(page: Page) {
  await page.goto("/es/products/perfume-e2e");
  await page
    .getByRole("button", { name: "Agregar al carrito", exact: true })
    .click();
  await expect(page.locator(".cart-link [data-cart-count]")).toHaveText("1");
  await expect(page.locator("#cart-dialog")).toBeVisible();
}
async function fillCustomer(page: Page) {
  await page.locator('[name="cedula"]').fill("1712345678");
  await page.locator('[name="first_name"]').fill("Ana");
  await page.locator('[name="last_name"]').fill("Prueba");
  await page.locator('[name="phone"]').fill("593990000000");
  await page.locator('[name="email"]').fill("cliente@example.test");
  await page.locator("#province").selectOption({ label: "Pichincha" });
  await page.locator("#city").selectOption({ label: "Quito" });
  await expect(page.locator("#checkout-total")).toHaveText("$17.75");
}
async function signIn(page: Page, target: string) {
  await page.goto(target);
  await expect(page).toHaveURL(/\/es\/admin\/login/);
  await page
    .locator('[name="username"]')
    .fill(process.env.BERONT_E2E_USERNAME ?? "");
  await page
    .locator('[name="password"]')
    .fill(process.env.BERONT_E2E_PASSWORD ?? "");
  await page.getByRole("button", { name: "Ingresar", exact: true }).click();
  await expect(page).toHaveURL(/\/es\/admin\/(?!login)/);
  await page.goto(target);
}

test("el estudio de decants agrega al carrito, resume el total y permite ajustar el carrito", async ({
  page,
}) => {
  await page.goto("/es/catalog/decants");
  await expect(page.locator(".studio h1")).toBeVisible();
  const card = page.locator(".studio-card").filter({ hasText: "Perfume E2E" });
  await card.click();
  await expect(card).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("[data-scene-name]")).toHaveText("Perfume E2E");
  await expect(page.locator("[data-scene-price]")).toHaveText("$12.50");
  await page.locator("[data-add]").click();
  await expect(page.locator("#cart-dialog")).not.toBeVisible();
  await expect(page.locator(".cart-link [data-cart-count]")).toHaveText("1");
  await expect(page.locator("[data-summary]")).toContainText(
    "Llevas 1 producto",
  );
  await expect(page.locator("[data-summary-total]")).toHaveText("$12.50");
  await page.locator("[data-summary] [data-open-cart]").click();
  await expect(page.locator("#cart-dialog")).toBeVisible();
  await expect(page.locator("#cart-items .cart-row")).toHaveCount(1);
  await expect(page.locator("#cart-items .mini-vial")).toHaveCount(1);
  await expect(page.locator("#cart-total")).toHaveText("$12.50");
  await page.locator('#cart-items [data-step="1"]').click();
  await expect(page.locator("#cart-total")).toHaveText("$25.00");
  await page.keyboard.press("Escape");
  await expect(page.locator("[data-summary-total]")).toHaveText("$25.00");
  await page.locator(".cart-link").click();
  await page.locator("#clear-cart").click();
  await expect(page.locator("#cart-status")).toHaveText(
    "Tu carrito está vacío",
  );
  await expect(page.locator("#cart-summary")).toBeHidden();
});

test("el panel de accesibilidad ajusta texto, contraste y animaciones y lo recuerda", async ({
  page,
}) => {
  await page.goto("/es/catalog/decants");
  const root = page.locator("html");
  const size = () =>
    page.evaluate(() =>
      parseFloat(getComputedStyle(document.documentElement).fontSize),
    );
  expect(await size()).toBe(16);
  await page
    .getByRole("button", { name: "Accesibilidad", exact: true })
    .click();
  const panel = page.locator("#a11y-panel");
  await expect(panel).toBeVisible();
  await panel.getByRole("button", { name: "Muy grande", exact: true }).click();
  await panel.getByLabel("Alto contraste").check();
  await panel.getByLabel("Reducir animaciones").check();
  await expect(root).toHaveAttribute("data-text", "xlarge");
  await expect(root).toHaveAttribute("data-contrast", "high");
  await expect(root).toHaveAttribute("data-motion", "reduce");
  expect(await size()).toBe(20);
  await page.reload();
  await expect(root).toHaveAttribute("data-text", "xlarge");
  await expect(root).toHaveAttribute("data-contrast", "high");
  await page
    .getByRole("button", { name: "Accesibilidad", exact: true })
    .click();
  await panel.getByRole("button", { name: "Restablecer", exact: true }).click();
  await expect(root).not.toHaveAttribute("data-text", /.+/);
  await expect(root).not.toHaveAttribute("data-contrast", /.+/);
  expect(await size()).toBe(16);
});

test("el carrito cambia los mililitros de una línea sin perder la cantidad", async ({
  page,
}) => {
  await page.goto("/es/catalog/decants");
  await page.locator(".studio-card").filter({ hasText: "Perfume E2E" }).click();
  await page.locator("[data-add]").click();
  await page.locator(".cart-link").click();
  const row = page.locator("#cart-items .cart-row");
  await expect(row).toHaveCount(1);
  const pills = row.locator("[data-size]");
  if ((await pills.count()) > 1) {
    await pills.last().click();
    await expect(row.locator('[data-size][aria-pressed="true"]')).toHaveText(
      await pills.last().innerText(),
    );
    await expect(page.locator("#cart-total")).not.toHaveText("$12.50");
  }
  await page.locator("#clear-cart").click();
});

test("la compra registra un pedido consultable y el administrador lo procesa", async ({
  page,
}) => {
  test.setTimeout(120000);
  await page.goto("/es/checkout");
  await expect(page.locator("#checkout-empty")).toBeVisible();
  await addToCart(page);
  await page.getByRole("link", { name: "Continuar con la compra" }).click();
  await expect(page).toHaveURL(/\/es\/checkout/);
  await expect(page.locator("#pay-button")).toBeDisabled();
  await fillCustomer(page);
  await page.locator("#open-terms").click();
  await expect(page.locator("#terms-dialog")).toContainText(
    "Términos de prueba",
  );
  await page.keyboard.press("Escape");
  await expect(page.locator("#open-terms")).toBeFocused();
  await expect(page.locator("input[value=whatsapp]")).toBeDisabled();
  await expect(page.locator("#whatsapp-off")).toBeVisible();
  await page
    .locator("#receipt")
    .setInputFiles(process.env.BERONT_E2E_IMAGE ?? "");
  await page.locator("#accept-terms").check();
  await page.locator("#pay-button").click();
  await expect(page).toHaveURL(/\/es\/orders\?received=1/);
  await expect(page.locator("#order-code-value")).toHaveText(/^BRT-/);
  const code = (await page.locator("#order-code-value").textContent()) ?? "";
  expect(code).toMatch(/^BRT-[A-Za-z0-9_-]{24}$/);
  await expect(page.locator("#order-status")).toHaveText("Pago en revisión");
  await expect(page.locator(".cart-link [data-cart-count]")).toHaveText("0");
  await expect(page.locator("#order-total")).toHaveText("$17.75");
  expect(await page.locator("body").textContent()).not.toContain("1712345678");

  await page.goto("/es/orders");
  await page.locator("#tracking-code").fill("BRT-" + "x".repeat(24));
  await page.getByRole("button", { name: "Consultar pedido" }).click();
  await expect(page.locator("[data-form-error]").first()).toBeVisible();
  await page.locator("#tracking-code").fill(code);
  await page.getByRole("button", { name: "Consultar pedido" }).click();
  await expect(page.locator("#order-code-value")).toHaveText(code);

  await signIn(page, "/es/admin/orders");
  await page.locator("#order-search").fill(code);
  const row = page.locator("#order-list button").first();
  await expect(row).toContainText(code);
  await row.click();
  await expect(page.locator("#detail-code")).toHaveText(code);
  await expect(page.locator("#detail-customer")).toContainText("1712345678");
  await page.locator("#approve-payment").click();
  await expect(page.locator("#order-message")).toContainText(
    "existencias descontadas",
  );
  await expect(page.locator("#detail-status")).toHaveText("Preparando envío");
  await expect(page.locator("#approve-payment")).toBeDisabled();
  await page.locator("#next-status").selectOption({ label: "Enviado" });
  await page.locator('[name="guide"]').fill("GUIA-E2E");
  await page.locator('[name="tracking"]').fill("SEG-E2E");
  await page.getByRole("button", { name: "Actualizar pedido" }).click();
  await expect(page.locator("#detail-status")).toHaveText("Enviado");

  await page.goto("/es/orders");
  await page.locator("#tracking-code").fill(code);
  await page.getByRole("button", { name: "Consultar pedido" }).click();
  await expect(page.locator("#order-status")).toHaveText("Enviado");
  await expect(page.locator("#order-guide")).toHaveText("GUIA-E2E");
  await expect(page.locator("#order-tracking")).toHaveText("SEG-E2E");
});

test("la transferencia exige comprobante y deja el pedido en revisión", async ({
  page,
}) => {
  test.setTimeout(120000);
  await addToCart(page);
  await page.goto("/es/checkout");
  await fillCustomer(page);
  await page.locator("input[value=bank_transfer]").check();
  await expect(page.locator("#bank-details")).toContainText("000123");
  await page.locator("#accept-terms").check();
  await page.locator("#pay-button").click();
  await expect(page).toHaveURL(/\/es\/checkout/);
  await page
    .locator("#receipt")
    .setInputFiles(process.env.BERONT_E2E_IMAGE ?? "");
  await page.locator("#pay-button").click();
  await expect(page).toHaveURL(/\/es\/orders\?received=1/);
  await expect(page.locator("#order-status")).toHaveText("Pago en revisión");
});

test("la recuperación de código responde sin revelar pedidos ni códigos", async ({
  page,
}) => {
  await page.goto("/es/orders");
  await page.getByRole("button", { name: "Perdí mi código" }).click();
  await expect(page.locator("#recovery-dialog")).toBeVisible();
  await page.locator('#recovery-form [name="cedula"]').fill("0000000000");
  await page.locator("#recovery-submit").click();
  await expect(page.locator("#recovery-status")).toContainText(
    /correo registrado|min/,
  );
  expect(await page.locator("#recovery-status").textContent()).not.toMatch(
    /BRT-/,
  );
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Perdí mi código" }),
  ).toBeFocused();
});

test("configuración y biblioteca funcionan con la base real", async ({
  page,
}) => {
  test.setTimeout(120000);
  await signIn(page, "/es/admin/settings");
  await expect(page.locator("#list-categories")).toContainText("Árabe");
  await expect(page.locator("#list-categories")).toContainText("Casa E2E");
  await page.locator("#tab-categories").focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("#panel-audiences")).toBeVisible();
  await expect(page.locator("#list-audiences")).toContainText("Mujer");
  await expect(page.locator("#panel-categories")).toBeHidden();
  await page.locator("#tab-accords").click();
  const accord = "Amaderado " + Date.now();
  await page.locator('#form-accords [name="name_es"]').fill(accord);
  await page
    .locator('#form-accords [name="name_en"]')
    .fill("Woody " + Date.now());
  await page.locator("#form-accords button").click();
  await expect(page.locator("#list-accords")).toContainText(accord);
  await page.locator("#tab-presentations").click();
  await expect(page.locator("#list-presentations")).toContainText("100");
  await page.locator("#tab-delivery").click();
  await expect(page.locator("#list-cities")).toContainText("Quito");
  await page.locator("#tab-banks").click();
  await expect(page.locator("#list-banks")).toContainText("Banco de pruebas");
  await page.locator("#tab-flow").click();
  await expect(page.locator("#list-statuses")).toContainText("Enviado");
  await expect(page.locator("#list-transitions")).toContainText(
    "Permite pasar a:",
  );

  await page.goto("/es/admin/media");
  await page
    .locator("#media-upload")
    .setInputFiles(process.env.BERONT_E2E_IMAGE ?? "");
  await expect(page.locator("#media-count")).toHaveText("Fotografía cargada.");
  await page.locator("#media-gallery .media-card").first().click();
  await expect(page.locator("#asset-dialog")).toBeVisible();
  await page.locator("#perfume-search").fill("Perfume E2E");
  await expect(page.locator("#perfume-select")).toContainText("Perfume E2E");
  await page.getByRole("button", { name: "Vincular fotografía" }).click();
  await expect(page.locator("#asset-status")).toContainText(/vinculada/);
  await page.keyboard.press("Escape");
  await expect(
    page.locator("#media-gallery .media-card").first(),
  ).toBeFocused();
});

test("las vistas nuevas no se desbordan en los tamaños acordados", async ({
  page,
}) => {
  test.setTimeout(180000);
  const overflow = () =>
    page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  await addToCart(page);
  for (const width of [320, 390, 600, 840, 1200, 1600, 1920])
    for (const route of ["/es/checkout", "/es/orders", "/en/checkout"]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(route);
      await expect(page.locator("main h1")).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      expect(await overflow(), route + " " + width).toBe(false);
    }
  await signIn(page, "/es/admin/settings");
  for (const width of [320, 390, 600, 840, 1200, 1600, 1920])
    for (const route of [
      "/es/admin/settings",
      "/es/admin/media",
      "/es/admin/orders",
      "/en/admin/orders",
    ]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(route);
      await expect(page.locator("main h1")).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      expect(await overflow(), route + " " + width).toBe(false);
    }
});

test("acordes, usos y perfiles se asignan en el editor y filtran el catálogo", async ({
  page,
  browserName,
}) => {
  test.setTimeout(120000);
  const stamp = browserName + " " + Date.now();
  const options = [
    ["accords", "accord", "Fresco", "Fresh"],
    ["usages", "usage", "Diario", "Daily"],
    ["profiles", "profile", "Cítrico", "Citrus"],
  ] as const;
  await signIn(page, "/es/admin/settings");
  for (const [tab, , es, en] of options) {
    await page.locator("#tab-" + tab).click();
    await page.locator(`#form-${tab} [name="name_es"]`).fill(`${es} ${stamp}`);
    await page.locator(`#form-${tab} [name="name_en"]`).fill(`${en} ${stamp}`);
    await page.locator(`#form-${tab} button`).click();
    await expect(page.locator("#list-" + tab)).toContainText(`${es} ${stamp}`);
  }
  await page.goto("/es/admin/products?q=Perfume%20E2E");
  await page.getByRole("link", { name: "Editar", exact: true }).first().click();
  const slugs: string[] = [];
  for (const [, , es] of options) {
    const box = page.getByLabel(`${es} ${stamp}`, { exact: true });
    slugs.push((await box.getAttribute("value"))!);
    await box.check();
  }
  await page.locator('#product-form [type="submit"]').click();
  await expect(page.locator("#toast")).toHaveText("Cambios guardados.");

  const query = options
    .map(([, param], index) => `${param}=${slugs[index]}`)
    .join("&");
  await page.goto("/es/catalog/decants?" + query);
  await expect(page.locator(".studio-card")).toHaveCount(1);
  await expect(page.locator(".studio-card")).toContainText("Perfume E2E");
  await page.locator(".studio-card").click();
  await expect(page.locator("[data-scene-meta]")).toContainText("Árabe");
  for (const [, param, es] of options)
    await expect(
      page.locator(`input[name="${param}"]:checked + span`),
    ).toHaveText(`${es} ${stamp}`);
  await page.goto("/es/catalog/decants?accord=no-existe");
  await expect(page.locator(".studio-card")).toHaveCount(0);

  await page.goto("/es/products/perfume-e2e");
  for (const [, , es] of options)
    await expect(page.locator(".attributes")).toContainText(`${es} ${stamp}`);
  await expect(page.locator(".attributes")).toContainText("Unisex");
  await page.goto("/en/products/perfume-e2e");
  for (const [, , , en] of options)
    await expect(page.locator(".attributes")).toContainText(`${en} ${stamp}`);
  await expect(page.locator(".attributes")).toContainText("Arabic");

  await page.goto("/es/admin/settings");
  await page.locator("#tab-accords").click();
  const row = page
    .locator("#list-accords li")
    .filter({ hasText: `Fresco ${stamp}` });
  await row.getByRole("button", { name: "Desactivar", exact: true }).click();
  await expect(row).toContainText("Inactivo");
  await page.goto("/es/catalog/decants");
  await expect(
    page.locator(`input[name="accord"][value="${slugs[0]}"]`),
  ).toHaveCount(0);
  await page.goto("/es/products/perfume-e2e");
  await expect(page.locator(".attributes")).not.toContainText(
    `Fresco ${stamp}`,
  );
});
