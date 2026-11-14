import { describe, test, expect } from "bun:test";
import { parsePerfume } from "../../src/features/catalog/perfume";
import { levelFor, vivid, css } from "../../src/shared/components/vial";
import { validateQuote } from "../../src/features/cart/quote";
import type { Quote } from "../../src/shared/http/contracts";
const base = {
  slug: "afnan-9pm",
  name: "9PM",
  brand: "Afnan",
  category: "Árabe",
  audience: "Hombre",
  image: { url: "/media/" + "a".repeat(32) + ".webp", alt: "Afnan 9PM" },
  variants: [
    {
      id: "d4f8c5e0-5d30-43d4-89d2-cd7aa94101af",
      volume: "5.00",
      price: "6.49",
      available: true,
    },
  ],
};
describe("estudio de decants", () => {
  test("acepta el formato del servidor y descarta datos manipulados", () => {
    expect(parsePerfume(JSON.stringify(base))?.name).toBe("9PM");
    expect(
      parsePerfume(JSON.stringify({ ...base, image: null })),
    ).not.toBeNull();
    expect(parsePerfume("no es json")).toBeNull();
    expect(parsePerfume(undefined)).toBeNull();
    expect(parsePerfume(JSON.stringify({ ...base, slug: 3 }))).toBeNull();
    expect(
      parsePerfume(
        JSON.stringify({
          ...base,
          variants: [{ id: "x", volume: "5", price: "1", available: "yes" }],
        }),
      ),
    ).toBeNull();
  });
  test("el nivel del frasco crece con los mililitros y se mantiene visible", () => {
    expect(levelFor(3, 10)).toBeCloseTo(0.41);
    expect(levelFor(10, 10)).toBeCloseTo(0.9);
    expect(levelFor(20, 10)).toBeCloseTo(0.9);
    expect(levelFor(5, 0)).toBe(0.5);
    expect(levelFor(1, 30)).toBeGreaterThan(0.2);
  });
  test("el color del líquido se vuelve vivo sin salir de rango", () => {
    for (const color of [
      [10, 10, 10],
      [240, 240, 240],
      [90, 120, 130],
    ] as const) {
      const out = vivid([...color]);
      for (const channel of out) {
        expect(channel).toBeGreaterThanOrEqual(0);
        expect(channel).toBeLessThanOrEqual(255);
      }
    }
    expect(css([1, 2, 3], 0.5)).toBe("rgb(1 2 3 / 0.5)");
  });
  test("la cotización acepta foto y presentaciones hermanas y rechaza rutas ajenas", () => {
    const quote = (line: object): Quote => ({
      currency: "USD",
      total: "6.49",
      whatsapp_url: null,
      configuration_error: null,
      items: [
        {
          variant_id: base.variants[0]!.id,
          quantity: 1,
          brand_name: "Afnan",
          product_name: "9PM",
          kind: "decant",
          volume_ml: "5.00",
          unit_price: "6.49",
          line_total: "6.49",
          ...line,
        },
      ],
    });
    const options = [
      {
        variant_id: base.variants[0]!.id,
        volume_ml: "5.00",
        unit_price: "6.49",
      },
    ];
    expect(() =>
      validateQuote(
        quote({ image_url: base.image.url, options, product_slug: "x" }),
      ),
    ).not.toThrow();
    expect(() => validateQuote(quote({ image_url: null }))).not.toThrow();
    expect(() =>
      validateQuote(quote({ image_url: "https://evil.example/x.webp" })),
    ).toThrow();
    expect(() =>
      validateQuote(quote({ options: [{ variant_id: "x" }] })),
    ).toThrow();
  });
});
