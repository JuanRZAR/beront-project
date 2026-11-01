import { describe, test, expect } from "bun:test";
import { CartStore } from "../../src/features/cart/store";
import { decimalUnits, decimalString } from "../../src/features/admin/decimal";
import { safeJson } from "../../src/shared/http/serialization";
import { validateQuote, quoteFingerprint } from "../../src/features/cart/quote";
import type { Quote } from "../../src/shared/http/contracts";
const first = "d4f8c5e0-5d30-43d4-89d2-cd7aa94101af";
const second = "c35c7421-d729-4364-a948-6aa28e440b62";
function storage(initial = "[]") {
  let value = initial;
  return {
    getItem: () => value,
    setItem: (_key: string, newValue: string) => {
      value = newValue;
    },
  };
}
describe("carrito", () => {
  test("solo persiste identificadores y cantidades entre instancias", () => {
    const data = storage();
    const cart = new CartStore(data);
    cart.add(first, 2);
    cart.add(first, 3);
    expect(new CartStore(data).read()).toEqual([
      { variant_id: first, quantity: 5 },
    ]);
  });
  test("rechaza cantidades y límites inválidos", () => {
    const cart = new CartStore(storage());
    for (const quantity of [0, -1, 1.5, 21])
      expect(() => cart.add(first, quantity)).toThrow();
    cart.add(first, 20);
    expect(() => cart.add(first, 1)).toThrow();
    expect(() => cart.add("wrong-id", 1)).toThrow();
  });
  test("limpia datos manipulados y consolida duplicados", () => {
    const cart = new CartStore(
      storage(
        JSON.stringify([
          { variant_id: first, quantity: 10, price: "0.01" },
          { variant_id: first, quantity: 15 },
          { variant_id: second, quantity: true },
          { variant_id: "unknown", quantity: 1 },
        ]),
      ),
    );
    expect(cart.read()).toEqual([{ variant_id: first, quantity: 20 }]);
  });
  test("mantiene la selección en memoria si el almacenamiento falla", () => {
    const cart = new CartStore({
      getItem: () => {
        throw Error();
      },
      setItem: () => {
        throw Error();
      },
    });
    cart.add(first, 1);
    expect(cart.persistent).toBe(false);
    expect(cart.read()).toHaveLength(1);
    cart.quantity(first, 2);
    expect(cart.read()[0]?.quantity).toBe(2);
    cart.remove(first);
    expect(cart.read()).toEqual([]);
  });
  test("elimina y sincroniza cambios sin guardar precios", () => {
    const data = storage(),
      cart = new CartStore(data);
    cart.add(first, 1);
    cart.add(second, 2);
    const other = new CartStore(data);
    other.remove(first);
    cart.invalidate();
    expect(cart.read()).toEqual([{ variant_id: second, quantity: 2 }]);
  });
});
test("vista previa de inventario usa aritmética decimal exacta", () => {
  expect(decimalString(decimalUnits("0.10")! + decimalUnits("0.20")!)).toBe(
    "0.30",
  );
  expect(
    decimalString(decimalUnits("99999999.99")! + decimalUnits("0.01")!),
  ).toBe("100000000.00");
  expect(decimalString(decimalUnits("-5.50")!)).toBe("-5.50");
  expect(decimalUnits("NaN")).toBeNull();
  expect(decimalUnits("0.001")).toBeNull();
});
test("el JSON incrustado no permite cerrar su elemento script", () => {
  const serialized = safeJson({ name: "</script><script>alert(1)</script>" });
  expect(serialized).not.toContain("<");
  expect(JSON.parse(serialized).name).toBe(
    "</script><script>alert(1)</script>",
  );
});
test("las cotizaciones requieren moneda y decimales válidos", () => {
  const quote: Quote = {
    currency: "USD",
    items: [],
    total: "0.00",
    whatsapp_url: null,
    configuration_error: "WHATSAPP_NOT_CONFIGURED",
  };
  expect(validateQuote(quote)).toBe(quote);
  expect(() => validateQuote({ ...quote, total: "0.001" })).toThrow();
  expect(() =>
    validateQuote({ ...quote, whatsapp_url: "javascript:alert(1)" }),
  ).toThrow();
  expect(quoteFingerprint({ ...quote, total: "1.00" })).not.toBe(
    quoteFingerprint(quote),
  );
});
