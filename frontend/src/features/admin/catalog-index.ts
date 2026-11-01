import { serverGet } from "../../shared/http/server";
import type { Product } from "../../shared/http/contracts";
export interface ProductLabel {
  name: string;
  brand: string;
  productId: string;
  volume?: string;
  kind?: string;
  available: boolean;
}
export async function catalogLabels(cookie: string) {
  const result = new Map<string, ProductLabel>();
  let page = 1;
  for (;;) {
    const response = await serverGet<Product[]>(
      "/api/v1/admin/products?page_size=48&page=" + page,
      cookie,
    );
    for (const product of response.data) {
      result.set(product.id, {
        name: product.name,
        brand: product.brand.name,
        productId: product.id,
        available: product.variants.some(
          (v) => v.kind === "decant" && v.available,
        ),
      });
      for (const variant of product.variants)
        result.set(variant.id, {
          name: product.name,
          brand: product.brand.name,
          productId: product.id,
          volume: variant.volume_ml,
          kind: variant.kind,
          available: variant.available,
        });
    }
    if (!response.meta || page * response.meta.page_size >= response.meta.total)
      break;
    page++;
  }
  return result;
}
