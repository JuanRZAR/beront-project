import { test, expect } from "@playwright/test";
import imported from "../../public/temporal/catalog.json";

test("el catálogo temporal muestra imágenes, filtros, tamaños, carrito e idiomas", async ({
  page,
  browserName,
}) => {
  const errors: string[] = [],
    realApi: string[] = [],
    external: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.pathname.startsWith("/api/v1/")) realApi.push(url.pathname);
    if (!["localhost", "127.0.0.1"].includes(url.hostname))
      external.push(url.origin);
  });
  await page.goto("/temporal/catalog-import.html");
  await expect(page.locator("#result-count")).toHaveText("119 perfumes");
  await expect(page.locator(".product-card")).toHaveCount(24);
  const photo = page.locator(".product-card img").first();
  await photo.scrollIntoViewIfNeeded();
  await expect
    .poll(() => photo.evaluate((img) => (img as HTMLImageElement).naturalWidth))
    .toBeGreaterThan(0);
  await page.getByRole("button", { name: "9 PM Classic", exact: true }).click();
  await expect(page.locator("#product-dialog")).toBeVisible();
  await page.locator("#product-size").selectOption({ label: "3 ml" });
  await page.locator("#product-quantity").fill("2");
  await expect(page.locator("#product-price")).toHaveText("$3.50");
  await page
    .getByRole("button", { name: "Agregar al carrito", exact: true })
    .click();
  await page.locator("#open-cart").click();
  await expect(page.locator("#cart-total")).toHaveText("$7.00");
  await expect(
    page.getByRole("button", { name: "Continuar por WhatsApp" }),
  ).toBeDisabled();
  await page.locator('[data-close="cart-dialog"]').click();

  await page.locator('.catalog-tabs [data-kind="full_bottle"]').click();
  await expect(page.locator("#result-count")).toHaveText("24 perfumes");
  await page.getByRole("button", { name: "9PM", exact: true }).click();
  await expect(page.locator("#product-size option")).toHaveText(["150 ml"]);
  await expect(page.locator("#product-price")).toHaveText("$76.00");
  await page
    .getByRole("button", { name: "Agregar al carrito", exact: true })
    .click();
  await page.locator("#open-cart").click();
  await expect(page.locator("#cart-total")).toHaveText("$83.00");
  await page.locator('[data-close="cart-dialog"]').click();
  await page.reload();
  await expect(page.locator("#cart-count")).toHaveText("3");
  await page.locator('[data-language="en"]').click();
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await page.locator("#open-cart").click();
  await expect(page.locator("#cart-title")).toHaveText("Cart");
  await expect(page.locator("#cart-total")).toHaveText("$83.00");
  await page.locator('[data-close="cart-dialog"]').click();

  await page.goto(
    "/temporal/catalog-import.html?kind=decant&q=Yara%20Candy&volume_ml=30.00&max_price=10.00",
  );
  await expect(page.locator("#result-count")).toHaveText("0 perfumes");
  await expect(page.locator("#catalog-status")).toHaveText(
    "No hay perfumes con estos filtros.",
  );
  await page.goto(
    "/temporal/catalog-import.html?kind=decant&q=Yara%20Candy&volume_ml=30.00",
  );
  await expect(page.locator(".product-card")).toHaveCount(1);
  await expect(page.locator(".price span")).toHaveText("$24.00");
  await page.getByRole("button", { name: "Yara Candy", exact: true }).click();
  await expect(page.locator("#product-size option")).toHaveText([
    "1 ml",
    "3 ml",
    "5 ml",
    "10 ml",
    "30 ml",
  ]);
  await page.keyboard.press("Escape");
  await expect(page.locator("#product-dialog")).not.toBeVisible();

  await page.goto("/temporal/catalog-import.html?kind=decant&q=Delina%20Eau");
  await expect(page.locator(".product-card")).toHaveCount(1);
  await expect(page.locator(".import-fallback")).toHaveText(
    "Fotografía pendiente",
  );

  await page.goto("/temporal/catalog-import.html");
  await expect(page.locator(".product-card")).toHaveCount(24);
  for (const width of [320, 360, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.locator(".import-name").first().click();
    await expect(page.locator("#product-dialog")).toBeVisible();
    expect(
      await page
        .locator("#product-dialog")
        .evaluate((el) => el.scrollWidth <= el.clientWidth),
    ).toBe(true);
    await page.locator('[data-close="product-dialog"]').click();
    await page.locator("#open-cart").click();
    await expect(page.locator("#cart-total")).toHaveText("$83.00");
    expect(
      await page
        .locator("#cart-dialog")
        .evaluate((el) => el.scrollWidth <= el.clientWidth),
    ).toBe(true);
    await page.locator('[data-close="cart-dialog"]').click();
    if (width < 768) {
      await page.locator("#open-filters").click();
      await expect(page.locator("#filters")).toHaveClass(/is-open/);
      await page.locator("#close-filters").click();
      await expect(page.locator("#open-filters")).toBeFocused();
    }
  }
  if (browserName === "chromium") {
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.evaluate(async () => {
        for (const img of document.querySelectorAll("img")) {
          img.loading = "eager";
          await img.decode().catch(() => undefined);
        }
      });
      await page.screenshot({
        path: `../design/reviews/catalog-import-${width}.png`,
        fullPage: true,
      });
      await page.locator(".import-name").first().click();
      await expect(page.locator("#product-dialog")).toBeVisible();
      await page.screenshot({
        path: `../design/reviews/catalog-import-product-${width}.png`,
      });
      await page.locator('[data-close="product-dialog"]').click();
      await page.locator("#open-cart").click();
      await expect(page.locator("#cart-total")).toHaveText("$83.00");
      await page.screenshot({
        path: `../design/reviews/catalog-import-cart-${width}.png`,
      });
      await page.locator('[data-close="cart-dialog"]').click();
    }
  }
  expect(errors).toEqual([]);
  expect(realApi).toEqual([]);
  expect(external).toEqual([]);
});

test("la API temporal sirve fotografías locales y rechaza precios o cantidades manipuladas", async ({
  request,
}) => {
  for (const image of imported.images) {
    const response = await request.head("/temporal/media/" + image.file);
    expect(response.status()).toBe(200);
    expect(response.headers()["content-type"]).toContain("image/webp");
  }
  const product = imported.products[0]!;
  const variant = product.variants[0]!;
  const before = await request.get(
    "/temporal/api/v1/catalog/products/" + product.id,
  );
  for (const item of [
    { variant_id: variant.id, quantity: 1, price: "0.01" },
    { variant_id: variant.id, quantity: -1 },
    { variant_id: variant.id, quantity: 1.5 },
  ]) {
    expect(
      (
        await request.post("/temporal/api/v1/cart/quote", {
          data: { items: [item] },
        })
      ).status(),
    ).toBe(422);
  }
  expect(
    (
      await request.post("/temporal/api/v1/cart/quote", {
        data: { items: [{ variant_id: variant.id, quantity: 1 }] },
      })
    ).status(),
  ).toBe(200);
  const after = await request.get(
    "/temporal/api/v1/catalog/products/" + product.id,
  );
  expect(await after.json()).toEqual(await before.json());
  expect((await request.get("/temporal/api/v1/admin/products")).status()).toBe(
    404,
  );
  expect(
    (
      await request.post("/temporal/api/v1/admin/products", { data: {} })
    ).status(),
  ).toBe(405);
});
