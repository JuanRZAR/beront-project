import { test, expect } from "@playwright/test";

test.setTimeout(60000);

for (const width of [320, 360, 390, 768, 1024, 1440, 1920]) {
  test(`solo accesibilidad reduce las animaciones del sitio a ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/es/");
    const root = page.locator("html");
    const toggle = page.locator("[data-home-toggle]");
    const carousel = page.locator("[data-home-carousel]");
    const panel = page.locator("#a11y-panel");
    const motion = panel.locator("[data-motion]");
    await expect(toggle).toBeEnabled();
    await expect(carousel).toHaveAttribute("data-playing", "");
    await expect(page.locator(".home-progress i")).toHaveCSS(
      "animation-name",
      "home-progress",
    );
    await expect(page.locator(".home-slide").first()).not.toHaveCSS(
      "transition-duration",
      "0s",
    );
    for (const reducedMotion of ["no-preference", "reduce"] as const) {
      await page.emulateMedia({ reducedMotion });
      await expect(toggle).toBeEnabled();
      await expect(carousel).toHaveAttribute("data-playing", "");
    }
    await page
      .getByRole("button", { name: "Accesibilidad", exact: true })
      .click();
    await expect(motion).not.toBeChecked();
    await motion.check();
    await expect(root).toHaveAttribute("data-motion", "reduce");
    await expect(toggle).toBeDisabled();
    await expect(page.locator(".home-progress i")).toHaveCSS(
      "animation-name",
      "none",
    );
    await expect(page.locator(".home-slide").first()).toHaveCSS(
      "transition-duration",
      "0s",
    );
    await motion.uncheck();
    await expect(toggle).toBeEnabled();
    await expect(carousel).toHaveAttribute("data-playing", "");
    await motion.check();
    await page.reload();
    await expect(root).toHaveAttribute("data-motion", "reduce");
    await expect(toggle).toBeDisabled();

    await page.goto("/es/catalog/decants");
    const wave = page.locator(".vial .wave-front").first();
    await expect(wave).toHaveCSS("animation-name", "none");
    await page
      .getByRole("button", { name: "Accesibilidad", exact: true })
      .click();
    await expect(motion).toBeChecked();
    await motion.uncheck();
    await expect(root).toHaveAttribute("data-motion", "full");
    await expect(wave).toHaveCSS("animation-name", "wave");
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(width);

    await page.goto("/es/catalog/full-bottles");
    const bottle = page.locator(".cyl-item").first();
    await expect(root).toHaveAttribute("data-motion", "full");
    await expect(bottle).not.toHaveCSS("transition-duration", "0s");
    await page
      .getByRole("button", { name: "Accesibilidad", exact: true })
      .click();
    await expect(motion).not.toBeChecked();
    await motion.check();
    await expect(bottle).toHaveCSS("transition-duration", "0s");
    await panel
      .getByRole("button", { name: "Restablecer", exact: true })
      .click();
    await expect(motion).not.toBeChecked();
    await expect(root).not.toHaveAttribute("data-motion", /.+/);
    await expect(bottle).not.toHaveCSS("transition-duration", "0s");
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(width);

    await page.goto("/en/");
    await expect(toggle).toBeEnabled();
    await expect(carousel).toHaveAttribute("data-playing", "");
    await expect(page.locator(".home-progress i")).toHaveCSS(
      "animation-name",
      "home-progress",
    );
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(width);
  });
}
