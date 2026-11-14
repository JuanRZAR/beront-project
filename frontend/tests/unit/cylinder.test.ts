import { describe, test, expect } from "bun:test";
import {
  itemPlacement,
  wrapDistance,
} from "../../src/features/catalog/cylinder-layout";
describe("carrusel cilíndrico", () => {
  test("la distancia circular elige siempre el camino más corto", () => {
    expect(wrapDistance(0, 0, 24)).toBe(0);
    expect(wrapDistance(1, 0, 24)).toBe(1);
    expect(wrapDistance(23, 0, 24)).toBe(-1);
    expect(wrapDistance(0, 23, 24)).toBe(1);
    expect(wrapDistance(12, 0, 24)).toBe(12);
    expect(wrapDistance(2, 4, 5)).toBe(3 > 5 / 2 ? -2 : 3);
  });
  test("solo se muestran dos elementos a cada lado y el activo va al frente", () => {
    const centre = itemPlacement(0, 100);
    expect(centre.visible).toBe(true);
    expect(centre.layer).toBe(10);
    expect(centre.transform).toContain("translateX(0px)");
    expect(centre.transform).toContain("scale(1)");
    const side = itemPlacement(-2, 100);
    expect(side.visible).toBe(true);
    expect(side.transform).toContain("translateX(-200px)");
    expect(side.transform).not.toContain("rotate");
    expect(side.transform).not.toContain("translateZ");
    expect(side.transform).toContain("scale(0.9)");
    expect(itemPlacement(-1, 100).transform).toContain("scale(0.9)");
    expect(itemPlacement(1, 100).transform).toContain("scale(0.9)");
    expect(itemPlacement(2, 100).transform).toContain("scale(0.9)");
    expect(itemPlacement(3, 100).visible).toBe(false);
  });
});
