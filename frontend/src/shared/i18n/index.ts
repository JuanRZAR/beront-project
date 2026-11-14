import es from "./es";
import en from "./en";
import commerce from "./commerce";
import home from "./home";
import type { OptionRow } from "../http/contracts";

export type Locale = "es" | "en";
export const locales = ["es", "en"] as const;
export const isLocale = (value: unknown): value is Locale =>
  value === "es" || value === "en";
const dictionaries: Record<Locale, Record<string, string>> = { es, en };
const extra: Record<Locale, Record<string, string>> = {
  es: {
    menu: "Menú",
    mainMenu: "Menú principal",
    home: "Inicio",
    whatsappConfirmation:
      "Confirmaremos disponibilidad, pago y envío por WhatsApp.",
    preferences: "Preferencias",
    language: "Idioma",
    save: "Guardar",
    cartLimit:
      "Se permiten hasta 20 presentaciones y 20 unidades por presentación.",
    invalidPresentation:
      "Esa presentación no está configurada. Créala primero en Configuración.",
    orderTotalLimit: "El total supera el importe admitido por el sistema.",
    unexpectedReceipt:
      "El pago por WhatsApp no requiere adjuntar un comprobante.",
    activate: "Activar",
    deactivate: "Desactivar",
    inStock: "Con existencias",
    outOfStock: "Sin existencias",
    choosePresentation: "Presentación configurada",
    noPresentationsLeft:
      "Ya agregaste todas las presentaciones configuradas. Crea otras en Configuración.",
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
    previous: "Anterior",
    next: "Siguiente",
    page: "Página",
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
    noStock: "No hay existencias registradas.",
    noMovements: "Aún no hay movimientos.",
    photo: "Fotografía",
    deletePhoto: "Eliminar fotografía",
    altEs: "Texto alternativo en español",
    altEn: "Texto alternativo en inglés",
    position: "Orden",
    addVariant: "Crear presentación",
    variantCreated: "Presentación creada.",
    productStatus: "Publicación y disponibilidad",
    bottleStock: "Las existencias de botellas se registran por presentación.",
    inventorySearch: "Nombre del perfume",
    emptyCatalogHelp:
      "Pronto encontrarás aquí nuestros decants y perfumes completos.",
    lineUnavailable: "Esta presentación o cantidad ya no está disponible.",
    schemaError: "La respuesta no pudo verificarse. Inténtalo de nuevo.",
    studioTitle: "Llena tu frasco",
    studioTitleEmphasis: "a tu medida.",
    studioChooseSize: "Elige cuántos mililitros",
    studioHint:
      "También puedes tocar las marcas junto al frasco o arrastrar el líquido.",
    studioList: "Decants disponibles",
    studioSelected: "Perfume elegido",
    studioNothing: "Elige un perfume de la lista.",
    family: "Familia",
    publicLabel: "Público",
    allOption: "Todos",
    moreFilters: "Más filtros",
    viewProduct: "Ver ficha",
    added: "Agregado",
    summaryOne: "Llevas 1 producto",
    summaryMany: "Llevas {n} productos",
    summaryTotal: "total",
    loading: "Cargando…",
    sizeChoice: "Mililitros",
    fillLevel: "Nivel del frasco",
    changeSize: "Cambiar mililitros de",
    accessibility: "Accesibilidad",
    accessibilityHelp: "Se guarda en este navegador.",
    textSize: "Tamaño del texto",
    textNormal: "Normal",
    textLarge: "Grande",
    textXLarge: "Muy grande",
    highContrast: "Alto contraste",
    reduceMotion: "Reducir animaciones",
    resetAccessibility: "Restablecer",
    carousel: "Carrusel",
    slideOf: "{n} de {total}",
    chooseOne: "Elegir perfume",
  },
  en: {
    menu: "Menu",
    mainMenu: "Main menu",
    home: "Home",
    whatsappConfirmation:
      "We will confirm availability, payment and shipping on WhatsApp.",
    preferences: "Preferences",
    language: "Language",
    save: "Save",
    cartLimit:
      "Up to 20 presentations and 20 units per presentation are allowed.",
    invalidPresentation:
      "That presentation is not configured. Create it first in Settings.",
    orderTotalLimit: "The total exceeds the amount the system accepts.",
    unexpectedReceipt:
      "Payment via WhatsApp does not require attaching a receipt.",
    activate: "Activate",
    deactivate: "Deactivate",
    inStock: "In stock",
    outOfStock: "Out of stock",
    choosePresentation: "Configured presentation",
    noPresentationsLeft:
      "You already added every configured presentation. Create more in Settings.",
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
    previous: "Previous",
    next: "Next",
    page: "Page",
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
    noStock: "No stock has been recorded.",
    noMovements: "No movements have been recorded.",
    photo: "Photo",
    deletePhoto: "Delete photo",
    altEs: "Spanish alternative text",
    altEn: "English alternative text",
    position: "Order",
    addVariant: "Create presentation",
    variantCreated: "Presentation created.",
    productStatus: "Publication and availability",
    bottleStock: "Full bottle stock is recorded per presentation.",
    inventorySearch: "Fragrance name",
    emptyCatalogHelp:
      "Our decants and full bottles will be available here soon.",
    lineUnavailable: "This presentation or quantity is no longer available.",
    schemaError: "The response could not be verified. Please try again.",
    studioTitle: "Fill your vial",
    studioTitleEmphasis: "to your measure.",
    studioChooseSize: "Choose how many millilitres",
    studioHint:
      "You can also tap the marks next to the vial or drag the liquid.",
    studioList: "Available decants",
    studioSelected: "Selected perfume",
    studioNothing: "Choose a perfume from the list.",
    family: "Family",
    publicLabel: "For",
    allOption: "All",
    moreFilters: "More filters",
    viewProduct: "View details",
    added: "Added",
    summaryOne: "You have 1 product",
    summaryMany: "You have {n} products",
    summaryTotal: "total",
    loading: "Loading…",
    sizeChoice: "Millilitres",
    fillLevel: "Vial level",
    changeSize: "Change millilitres of",
    accessibility: "Accessibility",
    accessibilityHelp: "Saved in this browser.",
    textSize: "Text size",
    textNormal: "Normal",
    textLarge: "Large",
    textXLarge: "Extra large",
    highContrast: "High contrast",
    reduceMotion: "Reduce animations",
    resetAccessibility: "Reset",
    carousel: "Carousel",
    slideOf: "{n} of {total}",
    chooseOne: "Choose a fragrance",
  },
};
export function translate(locale: Locale) {
  return (key: string) =>
    home[locale][key] ??
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
export function definitionLabel(
  rows: OptionRow[] | undefined,
  slug: string,
  locale: Locale,
) {
  const row = rows?.find((item) => item.slug === slug);
  return row ? (locale === "en" ? row.name_en : row.name_es) : slug;
}
