import { expect, test } from "bun:test";
import imported from "../../public/temporal/catalog.json";
import {
  temporaryCatalog,
  temporaryProduct,
  temporaryQuote,
} from "../../src/features/catalog/temporary";

test("el catálogo importado conserva tamaños y no inventa existencias", () => {
  expect(imported.source.cards).toBe(143);
  expect(imported.products).toHaveLength(130);
  expect(imported.products.flatMap((p) => p.variants)).toHaveLength(400);
  const sizes = new Set(
    imported.products.flatMap((p) => p.variants.map((v) => v.volume_ml)),
  );
  for (const size of ["1.00", "3.00", "5.00", "10.00", "20.00", "30.00"])
    expect(sizes.has(size)).toBe(true);
  expect(imported.products.every((p) => p.stock_status === "unknown")).toBe(
    true,
  );
  expect(
    imported.products
      .flatMap((p) => p.images)
      .every((i) => /^\/temporal\/media\/[a-f0-9]{32}\.webp$/.test(i.url)),
  ).toBe(true);
});

test("precio y tamaño deben corresponder a la misma presentación", () => {
  const p = imported.products.find((p) => p.name === "Yara Candy")!;
  const result = temporaryCatalog(
    new URLSearchParams({
      q: "Yara Candy",
      kind: "decant",
      volume_ml: "30.00",
      max_price: "10.00",
    }),
  );
  expect(result.data).toHaveLength(0);
  const found = temporaryCatalog(
    new URLSearchParams({
      q: "Yara Candy",
      kind: "decant",
      volume_ml: "30.00",
      max_price: "25.00",
    }),
  );
  expect(found.data[0]?.id).toBe(p.id);
  expect(found.data[0]?.price_from).toBe("24.00");
  expect(found.data[0]?.variants).toHaveLength(1);
});

test("la cotización simulada usa los precios importados con precisión y no modifica datos", () => {
  const p = imported.products.find((p) => p.name === "Yara Candy")!;
  const variant = p.variants.find((v) => v.volume_ml === "1.00")!;
  const before = JSON.stringify(temporaryProduct(p.id));
  const quote = temporaryQuote({
    items: [
      { variant_id: variant.id, quantity: 2 },
      { variant_id: variant.id, quantity: 1 },
    ],
  });
  expect(quote.data.total).toBe("10.53");
  expect(quote.data.items).toHaveLength(1);
  expect(quote.data.whatsapp_url).toBeNull();
  expect(quote.data.stock_status).toBe("unknown");
  expect(JSON.stringify(temporaryProduct(p.id))).toBe(before);
  expect(() =>
    temporaryQuote({
      items: [{ variant_id: variant.id, quantity: 1, price: "0.01" }],
    }),
  ).toThrow();
});

test("la API temporal rechaza límites excedidos e identificadores inventados", () => {
  const variant = imported.products[0]!.variants[0]!;
  for (const quantity of [0, -1, 1.5, 21])
    expect(() =>
      temporaryQuote({ items: [{ variant_id: variant.id, quantity }] }),
    ).toThrow();
  expect(() =>
    temporaryQuote({
      items: [
        { variant_id: variant.id, quantity: 20 },
        { variant_id: variant.id, quantity: 1 },
      ],
    }),
  ).toThrow();
  expect(() =>
    temporaryQuote({
      items: [{ variant_id: crypto.randomUUID(), quantity: 1 }],
    }),
  ).toThrow();
  expect(() =>
    temporaryCatalog(new URLSearchParams({ min_price: "40", max_price: "10" })),
  ).toThrow();
  expect(() =>
    temporaryCatalog(new URLSearchParams({ page_size: "1000000" })),
  ).toThrow();
});
