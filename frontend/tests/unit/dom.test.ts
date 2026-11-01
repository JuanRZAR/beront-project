import { test, expect } from "bun:test";
import { slugify } from "../../src/shared/components/dom";

test("slugify genera identificadores estables sin acentos", () => {
  expect(slugify("Árabe")).toBe("arabe");
  expect(slugify("  Parfums de Marly  ")).toBe("parfums-de-marly");
  expect(slugify("Cítrico / Fresco")).toBe("citrico-fresco");
  expect(slugify("!!!")).toBe("");
  expect(slugify("a".repeat(100)).length).toBe(64);
});
