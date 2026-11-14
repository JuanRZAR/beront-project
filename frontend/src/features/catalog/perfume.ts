import { definitionLabel, type Locale } from "../../shared/i18n";
import type { Facets, Product, Variant } from "../../shared/http/contracts";
export interface Size {
  id: string;
  volume: string;
  price: string;
  available: boolean;
}
export interface Perfume {
  slug: string;
  name: string;
  brand: string;
  category: string;
  audience: string;
  image: { url: string; alt: string } | null;
  variants: Size[];
}
const text = (value: unknown) => typeof value === "string";
export function parsePerfume(raw: string | undefined): Perfume | null {
  try {
    const value = JSON.parse(raw ?? "");
    const image = value.image;
    if (
      !text(value.slug) ||
      !text(value.name) ||
      !text(value.brand) ||
      !text(value.category) ||
      !text(value.audience) ||
      (image !== null && !(text(image?.url) && text(image?.alt))) ||
      !Array.isArray(value.variants) ||
      !value.variants.every(
        (size: Size) =>
          text(size.id) &&
          text(size.volume) &&
          text(size.price) &&
          typeof size.available === "boolean",
      )
    )
      return null;
    return value as Perfume;
  } catch {
    return null;
  }
}

export function perfumePayload(
  product: Product,
  kind: Variant["kind"],
  definitions: Facets["definitions"],
  locale: Locale,
) {
  const image = product.images[0];
  return JSON.stringify({
    slug: product.slug,
    name: product.name,
    brand: product.brand.name,
    category: product.classifications
      .map((slug) => definitionLabel(definitions.categories, slug, locale))
      .join(" / "),
    audience: definitionLabel(definitions.audiences, product.audience, locale),
    image: image
      ? {
          url: image.url,
          alt:
            (locale === "en" ? image.alt_en || image.alt_es : image.alt_es) ||
            product.brand.name + " " + product.name,
        }
      : null,
    variants: product.variants
      .filter((variant) => variant.kind === kind)
      .sort((a, b) => Number(a.volume_ml) - Number(b.volume_ml))
      .map((variant) => ({
        id: variant.id,
        volume: variant.volume_ml,
        price: variant.price,
        available: variant.available,
      })),
  });
}
