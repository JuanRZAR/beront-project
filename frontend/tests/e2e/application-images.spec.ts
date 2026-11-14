import { readFile } from "node:fs/promises";
import { test, expect } from "@playwright/test";

test("las fotografías conservan el alfa y caben sin marcos en las vistas reales", async ({
  page,
  browserName,
}) => {
  test.setTimeout(120000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/es/admin/login");
  await page
    .locator('[name="username"]')
    .fill(process.env.BERONT_E2E_USERNAME!);
  await page
    .locator('[name="password"]')
    .fill(process.env.BERONT_E2E_PASSWORD!);
  await page.getByRole("button", { name: "Ingresar", exact: true }).click();
  await expect(page).toHaveURL(/\/es\/admin\/(?!login)/);
  const csrf = (await (await page.request.get("/api/v1/auth/csrf")).json()).data
    .csrf_token;
  const headers = { "X-CSRFToken": csrf };
  const facets = (
    await (await page.request.get("/api/v1/catalog/facets")).json()
  ).data;
  const name = "Frasco PNG " + browserName + " " + Date.now();
  const created = await page.request.post("/api/v1/admin/products", {
    headers,
    data: {
      brand_id: facets.brands[0].id,
      name,
      slug: "frasco-png-" + browserName + "-" + Date.now(),
      audience: "unisex",
    },
  });
  expect(created.status()).toBe(201);
  const product = (await created.json()).data;
  for (const [kind, volume_ml, price] of [
    ["decant", "5", "12.50"],
    ["full_bottle", "100", "120.00"],
  ]) {
    const response = await page.request.post(
      `/api/v1/admin/products/${product.id}/variants`,
      {
        headers,
        data: { kind, volume_ml, price },
      },
    );
    expect(response.status()).toBe(201);
  }
  const uploaded = await page.request.post(
    `/api/v1/admin/products/${product.id}/images`,
    {
      headers,
      multipart: {
        file: {
          name: "frasco.png",
          mimeType: "image/png",
          buffer: await readFile(process.env.BERONT_E2E_IMAGE!),
        },
        alt_es: "Frasco transparente de prueba",
        alt_en: "Transparent test bottle",
      },
    },
  );
  expect(uploaded.status()).toBe(201);
  const imageUrl = (await uploaded.json()).data.url;
  const published = await page.request.patch(
    `/api/v1/admin/products/${product.id}`,
    {
      headers,
      data: { version: product.version, published: true },
    },
  );
  expect(published.status()).toBe(200);
  const widths = [
    320, 360, 390, 412, 599, 600, 768, 820, 839, 840, 1024, 1200, 1440, 1600,
    1920,
  ];
  for (const kind of ["decants", "full-bottles"]) {
    await page.goto(`/es/catalog/${kind}?q=${encodeURIComponent(name)}`);
    if (kind === "decants") await page.locator(".studio-card").first().click();
    const photo = page.locator(
      kind === "decants" ? "[data-scene-photo]" : ".cyl-item[data-active] img",
    );
    await expect(photo).toHaveAttribute("src", imageUrl);
    await photo.evaluate((image: HTMLImageElement) => image.decode());
    expect(
      await photo.evaluate((image: HTMLImageElement) => {
        const canvas = document.createElement("canvas");
        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;
        const ctx = canvas.getContext("2d")!;
        ctx.drawImage(image, 0, 0);
        return [
          ctx.getImageData(0, 0, 1, 1).data[3],
          ctx.getImageData(1, 1, 1, 1).data[3],
        ];
      }),
    ).toEqual([0, 127]);
    for (const width of widths)
      for (const large of [false, true]) {
        await page.setViewportSize({ width, height: 1000 });
        await page.evaluate((large) => {
          document.documentElement.dataset.text = large ? "xlarge" : "";
        }, large);
        const geometry = await photo.evaluate((image: HTMLImageElement) => {
          const box = image.parentElement!;
          const a = image.getBoundingClientRect(),
            b = box.getBoundingClientRect();
          const style = getComputedStyle(box),
            appearance = getComputedStyle(image);
          return {
            width: innerWidth,
            scroll: document.documentElement.scrollWidth,
            top: a.top - b.top,
            bottom: b.bottom - a.bottom,
            background: style.backgroundColor,
            shadow: style.boxShadow,
            radius: style.borderRadius,
            blend: appearance.mixBlendMode,
            filter: appearance.filter,
          };
        });
        expect(geometry.scroll).toBeLessThanOrEqual(geometry.width);
        expect(geometry.top).toBeGreaterThanOrEqual(-1);
        expect(geometry.bottom).toBeGreaterThanOrEqual(-1);
        expect(geometry.background).toBe("rgba(0, 0, 0, 0)");
        expect(geometry.shadow).toBe("none");
        expect(geometry.radius).toBe("0px");
        expect(geometry.blend).toBe("normal");
        expect(geometry.filter).toBe("none");
      }
  }
  await page.goto(`/es/products/${product.slug}?kind=decant`);
  await expect(page.locator("#product-gallery img")).toHaveAttribute(
    "src",
    imageUrl,
  );
  await page.locator("#product-gallery img").click();
  await expect(page.locator("#product-gallery img")).toHaveAttribute(
    "src",
    imageUrl,
  );
});
