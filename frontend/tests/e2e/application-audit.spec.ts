import { test, expect, type Route } from "@playwright/test";

test("un fallo tardío de un filtro anterior no reemplaza el filtro vigente", async ({
  page,
}) => {
  await page.goto("/es/catalog/decants");
  let previous: Route | undefined;
  let release!: () => void;
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  let intercepted = false;
  await page.route("**/es/catalog/decants?**", async (route) => {
    if (
      new URL(route.request().url()).searchParams.get("q") === "anterior" &&
      !intercepted
    ) {
      intercepted = true;
      previous = route;
      await held;
      await route.abort("failed").catch(() => {});
    } else await route.continue();
  });
  const search = page.getByRole("searchbox");
  await search.fill("anterior");
  await expect.poll(() => !!previous).toBe(true);
  await search.fill("Perfume E2E");
  await expect(page).toHaveURL(/q=Perfume\+E2E/);
  release();
  await page.waitForLoadState("networkidle");
  await expect(page).toHaveURL(/q=Perfume\+E2E/);
  await expect(page.locator(".studio-card")).toHaveCount(1);
});

test("cambiar una cantidad comparte la cotización entre el diálogo y el resumen", async ({
  page,
}) => {
  await page.goto("/es/catalog/decants");
  await page.locator(".studio-card").filter({ hasText: "Perfume E2E" }).click();
  await page.locator("[data-add]").click();
  await page.locator(".cart-link").click();
  await expect(page.locator("#cart-total")).toHaveText("$12.50");
  await page.waitForLoadState("networkidle");
  let quotes = 0;
  page.on("request", (request) => {
    if (request.url().endsWith("/api/v1/cart/quote")) quotes++;
  });
  await page.locator('#cart-items [data-step="1"]').click();
  await expect(page.locator("#cart-total")).toHaveText("$25.00");
  await page.waitForLoadState("networkidle");
  expect(quotes).toBe(1);
});
