import { test, expect } from "@playwright/test";

test("gestión real, inventario, imágenes y carrito sin reservar", async ({
  page,
  browserName,
}) => {
  test.setTimeout(90000);
  const name = "Perfume de prueba " + browserName + " " + Date.now();
  await page.goto("/es/admin/products");
  await expect(page).toHaveURL(/\/es\/admin\/login/);
  await page
    .locator('[name="username"]')
    .fill(process.env.BERONT_E2E_USERNAME ?? "");
  await page
    .locator('[name="password"]')
    .fill(process.env.BERONT_E2E_PASSWORD ?? "");
  await page.getByRole("button", { name: "Ingresar", exact: true }).click();
  await expect(page).toHaveURL(/\/es\/admin\/products/);
  await page.getByRole("link", { name: "Nuevo producto", exact: true }).click();
  await page
    .getByRole("button", { name: "Agregar casa comercial", exact: true })
    .click();
  await page
    .locator('#brand-form [name="name"]')
    .fill("Casa de prueba " + browserName + " " + Date.now());
  await page.locator('#brand-form [type="submit"]').click();
  await expect(page.locator("#brand-dialog")).not.toBeVisible();
  await page.locator("#edit-name").fill(name);
  await page
    .locator('[name="description_es"]')
    .fill("Texto <script>window.berontInjected=true</script>");
  await page
    .locator('[name="description_en"]')
    .fill("English fragrance description.");
  await page.locator('#product-form [type="submit"]').click();
  await expect(page).toHaveURL(/\/admin\/products\/[a-f0-9-]+\?created=1/);
  const editUrl = new URL(page.url()).pathname;
  const productId = editUrl.split("/").at(-1)!;
  const create = page.locator("#variant-create-form");
  await create.locator('[name="volume_ml"]').fill("7.50");
  await create.locator('[name="price"]').fill("9.99");
  await create.locator('[type="submit"]').click();
  await expect(page.locator(".variant-form[data-variant-id]")).toHaveCount(1);
  const decantId = await page
    .locator(".variant-form[data-variant-id]")
    .first()
    .getAttribute("data-variant-id");
  await create.locator('[name="kind"]').selectOption("full_bottle");
  await create.locator('[name="volume_ml"]').fill("100");
  await create.locator('[name="price"]').fill("100.00");
  await create.locator('[type="submit"]').click();
  await expect(page.locator(".variant-form[data-variant-id]")).toHaveCount(2);
  const bottleId = await page
    .locator(".variant-form[data-variant-id]")
    .last()
    .getAttribute("data-variant-id");
  await page.locator('#product-form [name="published"]').check();
  await page.locator('#product-form [type="submit"]').click();
  await expect(page.locator("#toast")).toHaveText("Cambios guardados.");
  await page
    .locator('#image-upload-form [name="file"]')
    .setInputFiles(process.env.BERONT_E2E_IMAGE!);
  await page
    .locator('#image-upload-form [name="alt_es"]')
    .fill("Fotografía de pruebas");
  await page.locator('#image-upload-form [type="submit"]').click();
  await expect(page.locator(".image-form[data-image-id]")).toHaveCount(1);
  await page.goto("/es/admin/inventory");
  let row = page.locator(".admin-table tbody tr").filter({ hasText: name });
  await row.getByRole("button", { name: "Ajustar", exact: true }).click();
  await page.locator("#stock-delta").fill("20");
  await page.locator("#stock-reason").fill("Saldo de pruebas");
  await page
    .getByRole("button", { name: "Registrar ajuste", exact: true })
    .click();
  await expect(page).toHaveURL(/updated=1/);
  await expect(page.locator("#stock-dialog")).not.toBeVisible();
  await page
    .getByRole("tab", { name: "Perfumes completos (unidades)", exact: true })
    .click();
  row = page.locator(".admin-table tbody tr").filter({ hasText: name });
  await row.getByRole("button", { name: "Ajustar", exact: true }).click();
  await page.locator("#stock-delta").fill("2");
  await page.locator("#stock-reason").fill("Saldo de botellas de pruebas");
  await page
    .getByRole("button", { name: "Registrar ajuste", exact: true })
    .click();
  await expect(page).toHaveURL(/updated=1/);
  await expect(page.locator("#stock-dialog")).not.toBeVisible();
  await page.goto("/es/catalog/decants?q=" + encodeURIComponent(name));
  await expect(page.locator(".product-card")).toHaveCount(1);
  await expect(page.locator(".card-sizes input")).toHaveCount(1);
  await expect(page.locator("[data-card-price]")).toHaveText("$9.99");
  await expect(
    page.locator("#hero-carousel .hero-slide:not([hidden]) img").first(),
  ).toHaveAttribute("src", /^\/media\/[a-f0-9]{32}\.webp$/);
  await page.locator(".product-card h3 a").click();
  const publicUrl = new URL(page.url()).pathname;
  await expect(page.locator(".sizes button")).toHaveText("7.50 ml");
  await expect(page.locator("#product-gallery img")).toHaveAttribute(
    "src",
    /^\/media\/[a-f0-9]{32}\.webp$/,
  );
  await expect(page.locator(".description")).toContainText("<script>");
  expect(
    await page.evaluate(() => Object.hasOwn(window, "berontInjected")),
  ).toBe(false);
  await page
    .getByRole("button", { name: "Agregar al carrito", exact: true })
    .click();
  await expect(page.locator(".cart-link [data-cart-count]")).toHaveText("1");
  await expect(page.locator("#cart-dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await page
    .locator(".presentation-kind a")
    .filter({ hasText: "Perfumes completos" })
    .click();
  await page
    .getByRole("button", { name: "Agregar al carrito", exact: true })
    .click();
  await expect(page.locator("#cart-items .cart-row")).toHaveCount(2);
  await expect(page.locator("#cart-total")).toHaveText("$109.99");
  await expect(page.locator("#continue-whatsapp")).toBeDisabled();
  await expect(page.locator("#whatsapp-unavailable")).toBeVisible();
  await page.keyboard.press("Escape");
  const inventory = await (
    await page.request.get("/api/v1/admin/inventory?page_size=48")
  ).json();
  expect(
    inventory.data.find(
      (item: { target_id: string }) => item.target_id === productId,
    ).amount,
  ).toBe("20.00");
  expect(
    inventory.data.find(
      (item: { target_id: string }) => item.target_id === bottleId,
    ).amount,
  ).toBe("2.00");
  await page.locator(".languages a").filter({ hasText: "EN" }).click();
  await page.locator(".cart-link").click();
  await expect(page.locator("#cart-title")).toHaveText("Cart");
  await expect(page.locator("#cart-total")).toHaveText("$109.99");
  await page.keyboard.press("Escape");
  const responsiveRoutes = [
    publicUrl,
    "/es/catalog/decants",
    "/es/checkout",
    "/es/admin/products?q=" + encodeURIComponent(name),
    editUrl,
    "/es/admin/inventory",
    "/es/admin/login",
  ];
  for (const width of [320, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const route of responsiveRoutes) {
      await page.goto(route);
      await expect(page.locator("main h1")).toBeVisible();
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth),
        route,
      ).toBeLessThanOrEqual(width);
      if (route.includes("/admin/products?q="))
        await expect(page.locator(".admin-table tbody tr")).toContainText(name);
    }
  }
  await page.setViewportSize({ width: 1280, height: 1000 });
  await page.goto(editUrl);
  const variant = page.locator(
    '.variant-form[data-variant-id="' + decantId + '"]',
  );
  await variant.locator('[name="price"]').fill("11.00");
  await variant.locator('[type="submit"]').click();
  await expect(page.locator("#toast")).toHaveText("Cambios guardados.");
  await page.goto(publicUrl);
  await page.locator(".cart-link").click();
  await expect(page.locator("#cart-total")).toHaveText("$111.00");
  await page.goto(editUrl);
  await page.locator('#product-form [name="sold_out"]').check();
  await page.locator('#product-form [type="submit"]').click();
  await expect(page.locator("#toast")).toHaveText("Cambios guardados.");
  await page.goto(publicUrl);
  await page.locator(".cart-link").click();
  await expect(page.locator("#cart-notice")).toContainText("disponibilidad");
  await expect(page.locator("#continue-whatsapp")).toBeDisabled();
  expect(
    await page.evaluate(
      () => JSON.parse(localStorage.getItem("beront.cart.v1") ?? "[]").length,
    ),
  ).toBe(2);
  await page.goto("/es/admin/products");
  await page.getByRole("button", { name: "Salir", exact: true }).click();
  await expect(page).toHaveURL(/\/admin\/login/);
  expect((await page.request.get("/api/v1/admin/inventory")).status()).toBe(
    401,
  );
  await page.goto("/en/admin/inventory");
  await expect(page).toHaveURL(/\/en\/admin\/login/);
});

test("rutas protegidas, CSRF y límites del proxy", async ({ request }) => {
  const redirect = await request.get("/es/admin/products", { maxRedirects: 0 });
  expect(redirect.status()).toBe(302);
  expect(redirect.headers()["cache-control"]).toBe("no-store");
  expect(redirect.headers()["x-frame-options"]).toBe("DENY");
  expect((await request.get("/api/v1/admin/products")).status()).toBe(401);
  expect(
    (
      await request.post("/api/v1/admin/brands", {
        data: { name: "Prohibited" },
      })
    ).status(),
  ).toBe(403);
  expect(
    (
      await request.post("/api/v1/cart/quote", {
        data: "x".repeat(65537),
        headers: { "Content-Type": "application/json" },
      })
    ).status(),
  ).toBe(413);
  expect((await request.get("/api/not-approved")).status()).toBe(404);
  expect([400, 403]).toContain(
    (await request.get("/es/", { headers: { Host: "evil.example" } })).status(),
  );
});
