import { test, expect } from "bun:test";
import { definitionLabel, translate } from "../../src/shared/i18n";
import { errorMessage, ApiError } from "../../src/shared/http/errors";
import type { OptionRow } from "../../src/shared/http/contracts";

const rows: OptionRow[] = [
  {
    id: "1",
    slug: "arabic",
    name_es: "Árabe",
    name_en: "Arabic",
    active: true,
    version: 1,
  },
];

test("las etiquetas vienen de las definiciones del backend", () => {
  expect(definitionLabel(rows, "arabic", "es")).toBe("Árabe");
  expect(definitionLabel(rows, "arabic", "en")).toBe("Arabic");
  expect(definitionLabel(rows, "nuevo", "es")).toBe("nuevo");
  expect(definitionLabel(undefined, "arabic", "es")).toBe("arabic");
});

test("los códigos de error del backend tienen mensaje propio", () => {
  const codes = [
    "CART_LIMIT",
    "INVALID_QUANTITY",
    "UNAVAILABLE_QUANTITY",
    "INVALID_PRESENTATION",
    "INVALID_VARIANT",
    "ORDER_TOTAL_LIMIT",
    "UNEXPECTED_RECEIPT",
  ];
  for (const locale of ["es", "en"] as const)
    for (const code of codes) {
      const body = { code, message: "", details: [] };
      expect(errorMessage(new ApiError(422, body), locale)).not.toBe(
        translate(locale)("requestFailed"),
      );
    }
});
