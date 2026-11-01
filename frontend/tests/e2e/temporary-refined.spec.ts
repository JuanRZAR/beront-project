import { test, expect } from "@playwright/test";

test("tres acciones llevan de una presentación visible al resumen de WhatsApp simulado", async ({
  page,
}) => {
  const errors: string[] = [],
    external: string[] = [],
    realApi: string[] = [];
  page.on("pageerror", (err) => errors.push(err.message));
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.pathname.startsWith("/api/v1/")) realApi.push(url.pathname);
    if (!["localhost", "127.0.0.1"].includes(url.hostname))
      external.push(url.origin);
  });
  await page.goto("/temporal/");
  const card = page
    .locator(".product-card")
    .filter({ has: page.locator(".import-name", { hasText: "9 PM Classic" }) });
  await expect(card).toBeVisible();
  let clicks = 0;
  await card.getByRole("radio", { name: "5 ml", exact: true }).check();
  clicks++;
  await expect(card.locator(".price span")).toHaveText("$5.25");
  await card.locator(".card-add").click();
  clicks++;
  await expect(page.locator("#cart-dialog")).toBeVisible();
  await expect(page.locator("#cart-total")).toHaveText("$5.25");
  await page.locator("#continue-whatsapp").click();
  clicks++;
  await expect(page.locator("#whatsapp-dialog")).toBeVisible();
  await expect(page.locator("#whatsapp-text")).toContainText("5 ml");
  await expect(page.locator("#whatsapp-text")).toContainText("$5.25");
  expect(clicks).toBe(3);
  expect(page.context().pages()).toHaveLength(1);
  expect(external).toEqual([]);
  expect(realApi).toEqual([]);
  expect(errors).toEqual([]);
  await page.keyboard.press("Escape");
  await expect(card.locator(".card-add")).toBeFocused();
});

test("carrusel, cantidades y filtros conservan acceso por teclado y límites", async ({
  page,
}) => {
  await page.goto("/temporal/");
  await expect(page.locator("#carousel-name")).not.toBeEmpty();
  const name = await page.locator("#carousel-name").textContent();
  await page.locator("#hero-carousel").focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("#carousel-name")).not.toHaveText(name!);
  await expect(page.locator("#hero-carousel")).toBeFocused();
  await page.keyboard.press("ArrowLeft");
  await expect(page.locator("#carousel-name")).toHaveText(name!);
  await page.locator("#carousel-dots button").nth(2).focus();
  await page.keyboard.press("Space");
  await expect(page.locator("#carousel-dots button").nth(2)).toBeFocused();
  await expect(page.locator("#carousel-slide")).toHaveAttribute(
    "aria-label",
    "3 / 3",
  );
  await page.waitForTimeout(400);
  await expect(page.locator("#carousel-slide")).toHaveAttribute(
    "aria-label",
    "3 / 3",
  );

  const card = page.locator(".product-card").first();
  await card.getByRole("button", { name: /^Aumentar cantidad/ }).click();
  await expect(card.getByRole("spinbutton")).toHaveValue("2");
  await card.locator(".card-add").click();
  await expect(page.locator("#cart-total")).toHaveText("$7.00");
  const plus = page
    .locator("#cart-items")
    .getByRole("button", { name: /^Aumentar cantidad/ });
  await plus.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#cart-total")).toHaveText("$10.50");
  await expect(plus).toBeFocused();
  const input = page.locator("#cart-items").getByRole("spinbutton");
  await input.fill("20");
  await input.press("Tab");
  await expect(page.locator("#cart-total")).toHaveText("$70.00");
  await expect(plus).toBeDisabled();
  await input.fill("21");
  await input.press("Tab");
  await expect(input).toHaveValue("20");
  await expect(page.locator("#toast")).toContainText("Máximo");
  await page.keyboard.press("Escape");

  await page.setViewportSize({ width: 390, height: 900 });
  await page.locator("#open-filters").click();
  await expect(page.locator("#filter-dialog")).toBeVisible();
  await expect(page.locator("#close-filters")).toBeFocused();
  await page.keyboard.press("Tab");
  expect(
    await page
      .locator("#filter-dialog")
      .evaluate((el) => el.contains(document.activeElement)),
  ).toBe(true);
  await page.keyboard.press("Escape");
  await expect(page.locator("#open-filters")).toBeFocused();
  await expect(page.locator("#catalog-body > #filters")).toHaveCount(1);
  await page.locator('[data-language="en"]').click();
  await expect(page.locator("#result-count")).toHaveText("119 fragrances");
  await page.locator("#open-cart").click();
  await expect(page.locator("#cart-title")).toHaveText("Cart");
  await expect(page.locator("#cart-total")).toHaveText("$70.00");
});

test("la revisión usa negro, controles amplios y vistas adaptables con fotografías integradas", async ({
  page,
  browserName,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (err) => errors.push(err.message));
  await page.goto("/temporal/");
  await expect(page.locator(".product-card")).toHaveCount(24);
  for (const selector of [".header-band", ".hero-band", ".site-footer"])
    await expect(page.locator(selector)).toHaveCSS(
      "background-color",
      "rgb(11, 11, 11)",
    );
  const first = page.locator(".product-card").first();
  await first.locator("img").evaluate(async (img) => {
    const el = img as HTMLImageElement;
    el.loading = "eager";
    await el.decode();
  });
  await expect
    .poll(() =>
      first
        .locator("img")
        .evaluate((el) =>
          Number((el as HTMLElement).style.getPropertyValue("--photo-light")),
        ),
    )
    .toBeGreaterThan(1);
  await expect(first.locator(".card-add")).toHaveCSS(
    "color",
    "rgb(11, 11, 11)",
  );
  for (const width of [320, 360, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    for (const selector of [
      ".card-add",
      ".quantity-stepper button",
      ".size-choice span",
    ]) {
      const bounds = await first.locator(selector).first().boundingBox();
      expect(bounds!.width).toBeGreaterThanOrEqual(44);
      expect(bounds!.height).toBeGreaterThanOrEqual(44);
    }
    await first.locator(".import-name").click();
    await expect(page.locator("#product-dialog")).toBeVisible();
    expect(
      await page
        .locator("#product-dialog")
        .evaluate((el) => el.scrollWidth <= el.clientWidth),
    ).toBe(true);
    await page.keyboard.press("Escape");
    if (width < 768) {
      await page.locator("#open-filters").click();
      expect(
        await page
          .locator("#filter-dialog")
          .evaluate((el) => el.scrollWidth <= el.clientWidth),
      ).toBe(true);
      await page.keyboard.press("Escape");
    }
  }
  if (browserName === "chromium") {
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1050 });
      await page.evaluate(() => scrollTo(0, 0));
      await page
        .locator("#hero-photos img")
        .evaluate((img) => (img as HTMLImageElement).decode());
      await page.screenshot({
        path: `../design/reviews/catalog-refined-${width}.png`,
      });
      await page.evaluate(async () => {
        for (const img of document.querySelectorAll(".product-card img")) {
          (img as HTMLImageElement).loading = "eager";
          await (img as HTMLImageElement).decode();
        }
      });
      await first.scrollIntoViewIfNeeded();
      await page.screenshot({
        path: `../design/reviews/catalog-refined-controls-${width}.png`,
      });
      await first.locator(".import-name").click();
      await expect(page.locator("#product-dialog")).toBeVisible();
      await page.screenshot({
        path: `../design/reviews/catalog-refined-product-${width}.png`,
      });
      await page.keyboard.press("Escape");
      await first.locator(".card-add").click();
      await expect(page.locator("#cart-total")).toHaveText("$3.50");
      await page.screenshot({
        path: `../design/reviews/catalog-refined-cart-${width}.png`,
      });
      await page.locator("#continue-whatsapp").click();
      await expect(page.locator("#whatsapp-dialog")).toBeVisible();
      await page.screenshot({
        path: `../design/reviews/catalog-refined-whatsapp-${width}.png`,
      });
      await page.keyboard.press("Escape");
      await page.locator("#open-cart").click();
      await page
        .getByRole("button", { name: "Vaciar carrito", exact: true })
        .click();
      await page.keyboard.press("Escape");
      await page.locator(".site-footer").scrollIntoViewIfNeeded();
      await page.screenshot({
        path: `../design/reviews/catalog-refined-footer-${width}.png`,
      });
    }
  }
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(page.locator("html")).toHaveCSS("scroll-behavior", "auto");
  expect(errors).toEqual([]);
});
