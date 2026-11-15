import { readFile } from "node:fs/promises";
import { test, expect } from "@playwright/test";

test.setTimeout(120000);

test("el Home muestra mensajes reales, enlaces, idiomas y tamaños adaptados", async ({
  page,
}) => {
  await page.addInitScript(() => {
    localStorage.setItem(
      "beront.a11y.v1",
      JSON.stringify({ motion: "reduce" }),
    );
  });
  await page.goto("/es/");
  const slides = page.locator("[data-home-slide]");
  await expect(slides).toHaveCount(5);
  await expect(page.locator("[data-home-slide][data-active]")).toContainText(
    "Una esencia.",
  );
  await expect(page.locator("main")).not.toContainText("Tu promoción");
  const widths = [
    320, 360, 390, 412, 599, 600, 768, 820, 839, 840, 1024, 1200, 1440, 1600,
    1920,
  ];
  for (const width of widths)
    for (const large of [false, true]) {
      await page.setViewportSize({ width, height: 900 });
      await page.evaluate((large) => {
        document.documentElement.dataset.text = large ? "xlarge" : "";
      }, large);
      for (let i = 0; i < 5; i++) {
        await page.locator("[data-home-dot]").nth(i).click();
        expect(
          await page.evaluate(() => document.documentElement.scrollWidth),
          `${width} ${large} ${i}`,
        ).toBeLessThanOrEqual(width);
        await expect(
          page.locator("[data-home-slide][data-active]"),
        ).toHaveAttribute("aria-hidden", "false");
        await expect(
          page.locator("[data-home-slide][data-active] a").first(),
        ).toBeVisible();
        expect(
          await page
            .locator("[data-home-slide]:not([data-active])")
            .evaluateAll((nodes) =>
              nodes.every((node) => (node as HTMLElement).inert),
            ),
        ).toBe(true);
      }
    }
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.evaluate(() => {
    document.documentElement.dataset.text = "";
  });
  await page.locator("[data-home-next]").focus();
  await page.keyboard.press("Home");
  await expect(slides.first()).toHaveAttribute("data-active", "");
  await page.keyboard.press("ArrowRight");
  await expect(slides.nth(1)).toHaveAttribute("data-active", "");
  await page.locator("[data-home-slide][data-active] a").first().click();
  await expect(page).toHaveURL(/\/es\/catalog\/decants/);
  await page.goto("/en/");
  await expect(page.locator("[data-home-slide][data-active]")).toContainText(
    "One essence.",
  );
  await expect(page.locator("[data-home-toggle]")).toBeDisabled();
});

test("el carrusel se pausa y respeta la reducción de movimiento", async ({
  page,
}) => {
  await page.clock.install();
  await page.goto("/es/");
  const slides = page.locator("[data-home-slide]");
  await page.clock.fastForward(7100);
  await expect(slides.nth(1)).toHaveAttribute("data-active", "");
  await page.locator("[data-home-toggle]").click();
  await page.mouse.move(0, 0);
  await page.clock.fastForward(15000);
  await expect(slides.nth(1)).toHaveAttribute("data-active", "");
  await page.locator("[data-home-toggle]").click();
  await page.mouse.move(0, 0);
  await page.clock.fastForward(7100);
  await expect(slides.nth(2)).toHaveAttribute("data-active", "");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(page.locator("[data-home-toggle]")).toBeEnabled();
  const next = slides.nth(3 % (await slides.count()));
  await page.clock.fastForward(7100);
  await expect(next).toHaveAttribute("data-active", "");
  await page
    .getByRole("button", { name: "Accesibilidad", exact: true })
    .click();
  await page.getByLabel("Reducir animaciones").check();
  await expect(page.locator("[data-home-toggle]")).toBeDisabled();
  await page.clock.fastForward(15000);
  await expect(next).toHaveAttribute("data-active", "");
});

test("configuración publica y desactiva mensajes con PNG transparente sin interpretar HTML", async ({
  page,
  browserName,
}) => {
  await page.goto("/es/admin/login");
  await page.locator("[name=username]").fill(process.env.BERONT_E2E_USERNAME!);
  await page.locator("[name=password]").fill(process.env.BERONT_E2E_PASSWORD!);
  await page.getByRole("button", { name: "Ingresar", exact: true }).click();
  await expect(page).toHaveURL(/\/es\/admin\/(?!login)/);
  const csrf = (await (await page.request.get("/api/v1/auth/csrf")).json()).data
    .csrf_token;
  const uploaded = await page.request.post("/api/v1/admin/media", {
    headers: { "X-CSRFToken": csrf },
    multipart: {
      name: "Frasco Home",
      file: {
        name: "frasco.png",
        mimeType: "image/png",
        buffer: await readFile(process.env.BERONT_E2E_IMAGE!),
      },
    },
  });
  expect([200, 201]).toContain(uploaded.status());
  const asset = (await uploaded.json()).data;
  await page.goto("/es/admin/settings");
  await page
    .getByRole("tab", { name: "Inicio y mensajes", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Nuevo mensaje", exact: true })
    .click();
  const form = page.locator("#home-message-form");
  const name = `Home ${browserName} ${Date.now()}`;
  const raw = `<img src=x onerror=window.homeInjected=1> ${name}`;
  for (const language of ["es", "en"]) {
    await form.locator(`[name=${language}_eyebrow]`).fill("Home");
    await form
      .locator(`[name=${language}_title]`)
      .fill(language === "es" ? raw : name);
    await form.locator(`[name=${language}_body]`).fill("Texto de prueba");
    await form.locator(`[name=${language}_primary_label]`).fill("Ver decants");
  }
  await form.locator("[name=active]").check();
  await page
    .locator("#home-media-options button")
    .filter({ hasText: asset.name })
    .first()
    .click();
  await form.getByRole("button", { name: "Guardar", exact: true }).click();
  await expect(page.locator("#home-message-status")).toHaveText(
    "Cambios guardados.",
  );
  await page.goto("/es/");
  const own = page.locator("[data-home-slide]").filter({ hasText: raw });
  const index = await own.evaluate((node) =>
    [...node.parentElement!.children].indexOf(node),
  );
  await page.locator("[data-home-dot]").nth(index).click();
  expect(await page.evaluate(() => Object.hasOwn(window, "homeInjected"))).toBe(
    false,
  );
  const image = own.locator("img");
  await image.evaluate((image: HTMLImageElement) => image.decode());
  expect(
    await image.evaluate((image: HTMLImageElement) => {
      const canvas = document.createElement("canvas");
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      const context = canvas.getContext("2d")!;
      context.drawImage(image, 0, 0);
      return [
        context.getImageData(0, 0, 1, 1).data[3],
        context.getImageData(1, 1, 1, 1).data[3],
      ];
    }),
  ).toEqual([0, 127]);
  await page.goto("/es/admin/settings");
  await page
    .getByRole("tab", { name: "Inicio y mensajes", exact: true })
    .click();
  await page
    .locator("#home-message-list")
    .getByRole("button", { name: raw, exact: true })
    .click();
  await form.locator("[name=active]").uncheck();
  await form.getByRole("button", { name: "Guardar", exact: true }).click();
  await expect(page.locator("#home-message-status")).toHaveText(
    "Cambios guardados.",
  );
  await page.goto("/es/");
  await expect(
    page.locator("[data-home-slide]").filter({ hasText: raw }),
  ).toHaveCount(0);
});
