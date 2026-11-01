import imported from "../../../public/temporal/catalog.json";

export type TemporaryProduct = (typeof imported.products)[number];
export type TemporaryVariant = TemporaryProduct["variants"][number];
const products = imported.products;
const normalize = (value: string) =>
  value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
const cents = (value: string) => BigInt(value.replace(".", ""));
const decimal = (value: bigint) =>
  `${value / 100n}.${String(value % 100n).padStart(2, "0")}`;

export class TemporaryError extends Error {
  constructor(
    public status: number,
    public code: string,
  ) {
    super(code);
  }
}

export function temporaryFacets() {
  return {
    brands: [
      ...new Map(products.map((p) => [p.brand.id, p.brand])).values(),
    ].sort((a, b) => a.name.localeCompare(b.name)),
    volumes_ml: [
      ...new Set(products.flatMap((p) => p.variants.map((v) => v.volume_ml))),
    ].sort((a, b) => Number(a) - Number(b)),
    classifications: ["arabic", "designer", "niche"],
    audiences: ["male", "female", "unisex"],
    kinds: ["decant", "full_bottle"],
  };
}

export function temporaryCatalog(query: URLSearchParams) {
  const allowed = [
    "q",
    "kind",
    "brand_id",
    "classification",
    "audience",
    "volume_ml",
    "min_price",
    "max_price",
    "sort",
    "page",
    "page_size",
    "locale",
  ];
  if ([...query.keys()].some((key) => !allowed.includes(key)))
    throw new TemporaryError(422, "VALIDATION_ERROR");
  const facets = temporaryFacets();
  for (const [key, values] of Object.entries({
    kind: facets.kinds,
    classification: facets.classifications,
    audience: facets.audiences,
    brand_id: facets.brands.map((b) => b.id),
    volume_ml: facets.volumes_ml,
    sort: ["name", "price_asc", "price_desc"],
    locale: ["es", "en"],
  })) {
    if (
      query
        .getAll(key)
        .filter(Boolean)
        .some((v) => !values.includes(v))
    )
      throw new TemporaryError(422, "VALIDATION_ERROR");
  }
  const amount = (key: string) => {
    const value = query.get(key);
    if (!value) return null;
    if (!/^\d{1,8}(?:\.\d{1,2})?$/.test(value))
      throw new TemporaryError(422, "VALIDATION_ERROR");
    return (
      BigInt(value.split(".")[0] ?? "0") * 100n +
      BigInt((value.split(".")[1] ?? "").padEnd(2, "0"))
    );
  };
  const min = amount("min_price"),
    max = amount("max_price");
  if (min !== null && max !== null && min > max)
    throw new TemporaryError(422, "VALIDATION_ERROR");
  const integer = (key: string, fallback: number, maximum: number) => {
    const value = query.get(key) || String(fallback);
    if (!/^\d+$/.test(value) || Number(value) < 1 || Number(value) > maximum)
      throw new TemporaryError(422, "VALIDATION_ERROR");
    return Number(value);
  };
  const page = integer("page", 1, 10000),
    pageSize = integer("page_size", 24, 48);
  const q = query.get("q") ?? "";
  if (q.length > 120) throw new TemporaryError(422, "VALIDATION_ERROR");
  const matches = (key: string, value: string) => {
    const selected = query.getAll(key).filter(Boolean);
    return !selected.length || selected.includes(value);
  };
  const result = products.flatMap((p) => {
    if (
      !normalize(`${p.brand.name} ${p.name}`).includes(normalize(q)) ||
      !matches("brand_id", p.brand.id) ||
      !matches("audience", p.audience) ||
      !p.classifications.some((value) => matches("classification", value))
    )
      return [];
    const variants = p.variants.filter(
      (v) =>
        matches("kind", v.kind) &&
        matches("volume_ml", v.volume_ml) &&
        (min === null || cents(v.price) >= min) &&
        (max === null || cents(v.price) <= max),
    );
    const first = variants[0];
    if (!first) return [];
    const priceFrom = variants.reduce(
      (a, v) => (cents(v.price) < cents(a) ? v.price : a),
      first.price,
    );
    return [
      { ...p, variants, price_from: priceFrom, currency: "USD" as const },
    ];
  });
  result.sort((a, b) => {
    const sort = query.get("sort");
    if (sort === "price_asc" || sort === "price_desc") {
      const difference = cents(a.price_from) - cents(b.price_from);
      if (difference)
        return (difference > 0n ? 1 : -1) * (sort === "price_desc" ? -1 : 1);
    }
    return `${a.brand.name} ${a.name}`.localeCompare(
      `${b.brand.name} ${b.name}`,
    );
  });
  return {
    data: result.slice((page - 1) * pageSize, page * pageSize),
    meta: { page, page_size: pageSize, total: result.length },
  };
}

export function temporaryProduct(id: string) {
  const product = products.find((p) => p.id === id);
  if (!product) throw new TemporaryError(404, "NOT_FOUND");
  return product;
}

export function temporaryQuote(body: unknown) {
  if (
    !body ||
    typeof body !== "object" ||
    !("items" in body) ||
    !Array.isArray(body.items) ||
    !body.items.length ||
    body.items.length > 100 ||
    Object.keys(body).some((key) => !["items", "locale"].includes(key)) ||
    ("locale" in body && !["es", "en"].includes(String(body.locale)))
  )
    throw new TemporaryError(422, "VALIDATION_ERROR");
  const quantities = new Map<string, number>();
  for (const item of body.items) {
    if (
      !item ||
      typeof item !== "object" ||
      typeof item.variant_id !== "string" ||
      !Number.isInteger(item.quantity) ||
      item.quantity < 1 ||
      item.quantity > 20 ||
      Object.keys(item).some((key) => !["variant_id", "quantity"].includes(key))
    )
      throw new TemporaryError(422, "VALIDATION_ERROR");
    quantities.set(
      item.variant_id,
      (quantities.get(item.variant_id) ?? 0) + item.quantity,
    );
  }
  if (quantities.size > 20 || [...quantities.values()].some((q) => q > 20))
    throw new TemporaryError(422, "CART_LIMIT");
  const items = [...quantities].map(([id, quantity]) => {
    const product = products.find((p) => p.variants.some((v) => v.id === id));
    const variant = product?.variants.find((v) => v.id === id);
    if (!product || !variant) throw new TemporaryError(409, "UNKNOWN_VARIANT");
    return {
      variant_id: id,
      quantity,
      brand_name: product.brand.name,
      product_name: product.name,
      kind: variant.kind,
      volume_ml: variant.volume_ml,
      unit_price: variant.price,
      line_total: decimal(cents(variant.price) * BigInt(quantity)),
    };
  });
  return {
    data: {
      currency: "USD",
      items,
      total: decimal(items.reduce((sum, i) => sum + cents(i.line_total), 0n)),
      stock_status: "unknown",
      whatsapp_url: null,
      configuration_error: "PREVIEW_ONLY",
    },
  };
}

export function temporaryOverview() {
  return {
    cards: imported.source.cards,
    products: products.length,
    decants: products.filter((p) => p.variants.some((v) => v.kind === "decant"))
      .length,
    bottles: products.filter((p) =>
      p.variants.some((v) => v.kind === "full_bottle"),
    ).length,
    images: imported.images.length,
    missing_images: products.filter((p) => !p.images.length).length,
  };
}
