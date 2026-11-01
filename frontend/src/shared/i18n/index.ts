import es from "./es";
import en from "./en";
import commerce from "./commerce";

export type Locale = "es" | "en";
export const locales = ["es", "en"] as const;
export const isLocale = (value: unknown): value is Locale =>
  value === "es" || value === "en";
const dictionaries: Record<Locale, Record<string, string>> = { es, en };
const extra: Record<Locale, Record<string, string>> = {
  es: {
    save: "Guardar",
    saved: "Cambios guardados.",
    created: "Producto creado. Añade presentaciones antes de publicarlo.",
    back: "Volver",
    archive: "Archivar",
    active: "Activo",
    inactive: "Inactivo",
    slug: "Identificador de URL",
    addHouse: "Agregar casa comercial",
    newHouse: "Nueva casa comercial",
    description: "Descripción",
    productUnavailable: "Este producto no está disponible.",
    imageUnavailable: "Imagen no disponible",
    requestFailed: "No se pudo completar la solicitud.",
    validation: "Revisa los campos indicados.",
    sessionExpired: "La sesión expiró. Ingresa de nuevo.",
    conflict: "Los datos cambiaron. Recarga antes de volver a guardar.",
    reload: "Recargar",
    selected: "Seleccionado",
    previous: "Anterior",
    next: "Siguiente",
    page: "Página",
    requiredReason: "Indica el motivo del ajuste.",
    inventorySaved: "Ajuste registrado.",
    unavailable: "No disponible",
    whatsappMissing:
      "Por ahora no es posible abrir WhatsApp. Inténtalo más tarde.",
    updatedPrice:
      "Los precios cambiaron. Revisa el nuevo total y vuelve a continuar.",
    checking: "Revisando precios y disponibilidad…",
    storageUnavailable:
      "Tu navegador conservará el carrito mientras esta página permanezca abierta.",
    csrf: "La sesión de seguridad expiró. Vuelve a intentarlo.",
    tooLarge: "El archivo o la solicitud excede el tamaño permitido.",
    badImage: "Utiliza una imagen JPEG, PNG o WebP válida.",
    retryLimit:
      "Se hicieron demasiados intentos. Espera antes de volver a intentar.",
    management: "Gestión del catálogo",
    noStock: "No hay existencias registradas.",
    noMovements: "Aún no hay movimientos.",
    loadInventory: "No pudimos cargar el inventario.",
    photo: "Fotografía",
    deletePhoto: "Eliminar fotografía",
    altEs: "Texto alternativo en español",
    altEn: "Texto alternativo en inglés",
    position: "Orden",
    addVariant: "Crear presentación",
    variantCreated: "Presentación creada.",
    viewPublic: "Ver en el catálogo",
    productStatus: "Publicación y disponibilidad",
    brandInactive: "Casa comercial inactiva",
    bottleStock: "Las existencias de botellas se registran por presentación.",
    inventorySearch: "Nombre del perfume",
    currentPage: "Página actual",
    totalRecords: "registros",
    loginHelp:
      "El administrador se crea mediante el acceso local del propietario.",
    emptyCatalog: "El catálogo se está preparando.",
    emptyCatalogHelp:
      "Pronto encontrarás aquí nuestros decants y perfumes completos.",
    filtersEmpty: "No hay opciones publicadas todavía.",
    reviewAvailability:
      "Revisa o elimina los productos que ya no están disponibles.",
    lineUnavailable: "Esta presentación o cantidad ya no está disponible.",
    schemaError: "La respuesta no pudo verificarse. Inténtalo de nuevo.",
  },
  en: {
    save: "Save",
    saved: "Changes saved.",
    created: "Product created. Add presentations before publishing.",
    back: "Back",
    archive: "Archive",
    active: "Active",
    inactive: "Inactive",
    slug: "URL identifier",
    addHouse: "Add fragrance house",
    newHouse: "New fragrance house",
    description: "Description",
    productUnavailable: "This product is not available.",
    imageUnavailable: "Image unavailable",
    requestFailed: "The request could not be completed.",
    validation: "Review the indicated fields.",
    sessionExpired: "Your session expired. Please sign in again.",
    conflict: "The data changed. Reload before saving again.",
    reload: "Reload",
    selected: "Selected",
    previous: "Previous",
    next: "Next",
    page: "Page",
    requiredReason: "Enter the reason for the adjustment.",
    inventorySaved: "Adjustment recorded.",
    unavailable: "Unavailable",
    whatsappMissing:
      "WhatsApp cannot be opened right now. Please try again later.",
    updatedPrice: "Prices changed. Review the new total and continue again.",
    checking: "Checking prices and availability…",
    storageUnavailable:
      "Your browser will keep the cart while this page remains open.",
    csrf: "Your security session expired. Please try again.",
    tooLarge: "The file or request exceeds the permitted size.",
    badImage: "Use a valid JPEG, PNG or WebP image.",
    retryLimit: "Too many attempts. Please wait before trying again.",
    management: "Catalog management",
    noStock: "No stock has been recorded.",
    noMovements: "No movements have been recorded.",
    loadInventory: "We could not load the inventory.",
    photo: "Photo",
    deletePhoto: "Delete photo",
    altEs: "Spanish alternative text",
    altEn: "English alternative text",
    position: "Order",
    addVariant: "Create presentation",
    variantCreated: "Presentation created.",
    viewPublic: "View in catalog",
    productStatus: "Publication and availability",
    brandInactive: "Inactive fragrance house",
    bottleStock: "Full bottle stock is recorded per presentation.",
    inventorySearch: "Fragrance name",
    currentPage: "Current page",
    totalRecords: "records",
    loginHelp: "The administrator is created through the owner's local access.",
    emptyCatalog: "Our catalog is being prepared.",
    emptyCatalogHelp:
      "Our decants and full bottles will be available here soon.",
    filtersEmpty: "No published options yet.",
    reviewAvailability:
      "Review or remove the products that are no longer available.",
    lineUnavailable: "This presentation or quantity is no longer available.",
    schemaError: "The response could not be verified. Please try again.",
  },
};
export function translate(locale: Locale) {
  return (key: string) =>
    commerce[locale][key] ??
    extra[locale][key] ??
    dictionaries[locale][key] ??
    key;
}
export function money(value: string) {
  return "$" + value;
}
export function number(value: string) {
  return value.replace(/\.00$/, "");
}
