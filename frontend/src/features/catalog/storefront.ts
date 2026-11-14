export const catalogOnly = import.meta.env.PUBLIC_CATALOG_ONLY !== "false";
export const cartEnabled = import.meta.env.PUBLIC_CART_ENABLED !== "false";

export function isStorefrontLink(path: string) {
  if (!catalogOnly) return true;
  const pathname = (path.split(/[?#]/, 1)[0] ?? path).replace(/\/$/, "") || "/";
  return (
    ["/", "/catalog/decants", "/catalog/full-bottles"].includes(pathname) ||
    pathname.startsWith("/products/")
  );
}
