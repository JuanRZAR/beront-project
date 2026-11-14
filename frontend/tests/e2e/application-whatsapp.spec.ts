import { test, expect } from "@playwright/test";

test.skip(
  process.env.BERONT_E2E_WHATSAPP_ONLY !== "true",
  "Requiere el perfil de solicitudes por WhatsApp.",
);

test("el catálogo permite agregar, ajustar y quitar productos y preparar WhatsApp con saldo cero", async ({
  page,
}) => {
  await page.goto("/es/catalog/decants");
  await expect(page.locator(".primary-nav a")).toHaveCount(3);
  await expect(page.locator(".stock-badge")).toHaveCount(0);
  await expect(page.locator('.site-header a[href$="/orders"]')).toHaveCount(0);
  await page.locator(".studio-card").filter({ hasText: "Perfume E2E" }).click();
  await page
    .locator("[data-sizes] button")
    .filter({ hasText: /^5 ml/ })
    .click();
  await expect(page.locator("[data-add]")).toBeEnabled();
  await page.locator("[data-add]").click();
  await expect(page.locator(".cart-link [data-cart-count]")).toHaveText("1");
  await page.goto("/es/catalog/full-bottles");
  await expect(page.getByText("Agotado", { exact: true })).toHaveCount(0);
  await page.locator("[data-add]").click();
  await page.locator(".cart-link").click();
  await expect(page.locator("#cart-total")).toHaveText("$132.50");
  await expect(page.locator("#continue-checkout")).toHaveCount(0);
  const decant = page.locator(".cart-row").filter({ hasText: "Decant" });
  await decant.locator('[data-step="1"]').click();
  await expect(page.locator("#cart-total")).toHaveText("$145.00");
  await decant.locator('[data-step="-1"]').click();
  await expect(page.locator("#cart-total")).toHaveText("$132.50");
  const bottle = page
    .locator(".cart-row")
    .filter({ hasText: "Botella completa" });
  await expect(bottle.locator(".cart-product-photo")).toBeVisible();
  await expect(bottle.locator(".mini-vial")).toHaveCount(0);
  await expect(decant.locator(".cart-product-photo")).toBeVisible();
  await expect(decant.locator(".mini-vial")).toHaveCount(1);
  for (const photo of await page.locator(".cart-product-photo").all()) {
    await expect(photo).toHaveAttribute("alt", "Casa E2E Perfume E2E");
    await photo.evaluate((image: HTMLImageElement) => image.decode());
  }
  await bottle.locator(".remove-item").click();
  await expect(page.locator("#cart-total")).toHaveText("$12.50");
  await page.reload();
  await page.locator(".cart-link").click();
  await expect(page.locator(".cart-row")).toHaveCount(1);
  await expect(page.locator("#cart-total")).toHaveText("$12.50");
  await page.keyboard.press("Escape");
  await page.goto("/en/");
  await page.locator(".cart-link").click();
  await expect(page.locator("#cart-total")).toHaveText("$12.50");
  await expect(page.locator("#continue-whatsapp")).toBeEnabled();
  const stored = await page.evaluate(() =>
    JSON.parse(localStorage.getItem("beront.cart.v1") ?? "[]"),
  );
  expect(Object.keys(stored[0]).sort()).toEqual(["quantity", "variant_id"]);
  let destination = "";
  await page.route("https://wa.me/**", async (route) => {
    destination = route.request().url();
    await route.fulfill({
      status: 200,
      contentType: "text/html",
      body: "<title>WhatsApp interceptado en prueba local</title>",
    });
  });
  await page.locator("#continue-whatsapp").click();
  await expect(page).toHaveURL(/^https:\/\/wa.me\/593939237376\?/);
  const link = new URL(destination);
  expect(link.searchParams.get("text")).toContain(
    "*1. Casa E2E — Perfume E2E*\nPresentation: Decant · 5 ml\nQuantity: 1\nUnit price: USD 12.50\nSubtotal: USD 12.50\n\n*Total: USD 12.50*",
  );
  expect(link.searchParams.get("text")).toContain("Total: USD 12.50");
  expect(link.searchParams.get("text")).toContain(
    "Availability and shipping to be confirmed.",
  );
});

test("el carrito conserva controles accesibles y cabe en los rangos de pantalla", async ({
  page,
}) => {
  test.setTimeout(90000);
  await page.goto("/es/products/perfume-e2e");
  await page.locator("#add-to-cart").click();
  await expect(page.locator("#cart-total")).toHaveText("$12.50");
  await page.keyboard.press("Escape");
  await page.goto("/es/products/perfume-e2e?kind=full_bottle");
  await page.locator("#add-to-cart").click();
  await expect(page.locator("#cart-total")).toHaveText("$132.50");
  await expect(page.locator(".cart-product-photo")).toHaveCount(2);
  for (const width of [320, 360, 390, 768, 1024, 1440, 1920, 2560]) {
    await page.setViewportSize({ width, height: width < 600 ? 740 : 900 });
    for (const largeText of [false, true]) {
      await page.evaluate((large) => {
        document.documentElement.dataset.text = large ? "xlarge" : "";
      }, largeText);
      const bounds = await page.locator("#cart-dialog").evaluate((dialog) => {
        const rect = dialog.getBoundingClientRect();
        return {
          left: rect.left,
          right: rect.right,
          width: innerWidth,
          overflow: dialog.scrollWidth > dialog.clientWidth + 1,
        };
      });
      expect(bounds.left).toBeGreaterThanOrEqual(0);
      expect(bounds.right).toBeLessThanOrEqual(bounds.width);
      expect(bounds.overflow).toBe(false);
      for (const row of await page.locator(".cart-row").all()) {
        await expect(row.locator(".remove-item")).toBeVisible();
        const layout = await row.evaluate((element) => {
          const image = element
            .querySelector(".cart-row-visual")!
            .getBoundingClientRect();
          const text = element
            .querySelector(".cart-row-main")!
            .getBoundingClientRect();
          return {
            right: image.right,
            text: text.left,
            overflow: element.scrollWidth > element.clientWidth + 1,
          };
        });
        expect(layout.right).toBeLessThanOrEqual(layout.text);
        expect(layout.overflow).toBe(false);
      }
      await page.locator("#continue-whatsapp").scrollIntoViewIfNeeded();
      await expect(page.locator("#continue-whatsapp")).toBeVisible();
    }
  }
  await page.keyboard.press("Escape");
  await expect(page.locator("#add-to-cart")).toBeFocused();
  await page.locator(".cart-link").focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#cart-dialog")).toBeVisible();
  await page.locator("#clear-cart").click();
  await expect(page.locator("#cart-summary")).toBeHidden();
  await expect(page.locator(".cart-link [data-cart-count]")).toHaveText("0");
});

test("el decant anima el líquido y actualiza su nivel al cambiar ml, respetando movimiento reducido", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/es/products/perfume-e2e");
  await page.locator("#add-to-cart").click();
  await expect(page.locator("#cart-total")).toHaveText("$12.50");
  const vial = page.locator("#cart-items .mini-vial");
  const firstLevel = await vial.evaluate((svg) =>
    svg.style.getPropertyValue("--drop"),
  );
  await page.locator('[data-size]:not([aria-pressed="true"])').click();
  await expect
    .poll(() => vial.evaluate((svg) => svg.style.getPropertyValue("--drop")))
    .not.toBe(firstLevel);
  await expect
    .poll(() =>
      vial
        .locator(".wave-front")
        .evaluate((wave) => getComputedStyle(wave).animationName),
    )
    .toBe("wave");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect
    .poll(() =>
      vial
        .locator(".wave-front")
        .evaluate((wave) => getComputedStyle(wave).animationName),
    )
    .toBe("none");
});

test("una foto que falla se indica sin sustituir un perfume completo por un decant", async ({
  page,
}) => {
  await page.route("**/media/**", (route) => route.abort());
  await page.goto("/es/products/perfume-e2e?kind=full_bottle");
  await page.locator("#add-to-cart").click();
  await expect(page.locator("#cart-total")).toHaveText("$120.00");
  await expect(page.locator(".cart-photo-missing")).toHaveText(
    "Imagen no disponible",
  );
  await expect(page.locator(".cart-product-photo")).toHaveCount(0);
  await expect(page.locator("#cart-items .mini-vial")).toHaveCount(0);
});
