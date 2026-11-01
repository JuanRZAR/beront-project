export interface ApiErrorBody {
  code: string;
  message: string;
  details: {
    field?: string;
    code?: string;
    variant_id?: string;
    seconds?: number;
  }[];
  request_id?: string;
}
export interface Envelope<T> {
  data: T;
  meta?: { page: number; page_size: number; total: number };
}
export interface Session {
  id: string;
  username: string;
  role: "admin";
  permissions: string[];
  csrf_token?: string;
}
export interface Brand {
  id: string;
  name: string;
  active?: boolean;
  version?: number;
  category_id?: string;
}
export interface Variant {
  id: string;
  kind: "decant" | "full_bottle";
  volume_ml: string;
  price: string;
  available: boolean;
  version?: number;
  active?: boolean;
  sold_out?: boolean;
  product_id?: string;
}
export interface ProductImage {
  id: string;
  url: string;
  position: number;
  alt_es: string;
  alt_en: string;
  version?: number;
}
export interface Product {
  id: string;
  name: string;
  slug: string;
  brand: Brand;
  audience: string;
  classifications: string[];
  description: string;
  description_locale: "es" | "en";
  variants: Variant[];
  images: ProductImage[];
  available: boolean;
  price_from: string | null;
  currency: "USD";
  version?: number;
  published?: boolean;
  archived?: boolean;
  sold_out?: boolean;
  description_es?: string;
  description_en?: string;
}
export interface ProductOptions {
  accords: string[];
  usages: string[];
  profiles: string[];
}
export interface Facets {
  brands: Brand[];
  volumes_ml: string[];
  classifications: string[];
  audiences: string[];
  kinds: string[];
}
export interface CartItem {
  variant_id: string;
  quantity: number;
}
export interface QuoteLine extends CartItem {
  brand_name: string;
  product_name: string;
  kind: Variant["kind"];
  volume_ml: string;
  unit_price: string;
  line_total: string;
}
export interface Quote {
  currency: "USD";
  items: QuoteLine[];
  total: string;
  whatsapp_url: string | null;
  configuration_error: string | null;
}
export interface Balance {
  id: string;
  target_id: string;
  kind: Variant["kind"];
  amount: string;
  version: number;
  unit: "ml" | "units";
}
export interface Movement {
  id: string;
  kind: Variant["kind"];
  target_id: string;
  delta: string;
  balance_after: string;
  version_after: number;
  reason: string;
  actor_id: string;
  operation_id: string;
  created_at: string;
}

export interface Province {
  id: string;
  code: string;
  name: string;
  mainland: boolean;
  active: boolean;
  version: number;
}
export interface City {
  id: string;
  province_id: string;
  name: string;
  shipping_fee: string;
  active: boolean;
  version: number;
}
export interface Bank {
  id: string;
  bank_name: string;
  account_type: string;
  account_number: string;
  holder_name: string;
  holder_identification: string;
  active: boolean;
  version: number;
}
export interface StoreSettings {
  id?: number;
  whatsapp_number: string;
  terms_es: string;
  terms_en: string;
  version: number;
}
export interface CheckoutOptions {
  settings: Pick<
    StoreSettings,
    "whatsapp_number" | "terms_es" | "terms_en"
  > | null;
  provinces: Province[];
  cities: City[];
  banks: Bank[];
}
export interface CheckoutQuote {
  currency: "USD";
  items: QuoteLine[];
  city_id: string;
  city_name: string;
  province_name: string;
  subtotal: string;
  shipping_fee: string;
  total: string;
  terms_text: string;
  banks: Bank[];
  quote_token: string;
}
export interface OrderStatus {
  id?: string;
  slug: string;
  name_es: string;
  name_en: string;
  phase:
    | "awaiting_payment"
    | "paid"
    | "shipped"
    | "delivered"
    | "cancelled"
    | "stock_issue";
  purpose?: string | null;
  active?: boolean;
  version?: number;
}
export interface OrderLine {
  product_name: string;
  brand_name: string;
  kind: Variant["kind"];
  volume_ml: string;
  quantity: number;
  unit_price: string;
  line_total: string;
}
export interface OrderHistory {
  name_es: string;
  name_en: string;
  created_at: string;
}
export interface PublicOrder {
  code: string;
  created_at: string;
  subtotal: string;
  shipping_fee: string;
  total: string;
  payment_method: "bank_transfer" | "whatsapp";
  payment_state: "pending" | "confirmed" | "stock_issue";
  guide_number: string;
  tracking_number: string;
  currency: "USD";
  delivery_mode: "address" | "agency";
  status: OrderStatus;
  items: OrderLine[];
  history: OrderHistory[];
  whatsapp_url: string | null;
}
export interface AdminOrder {
  id: string;
  code: string;
  created_at: string;
  version: number;
  cedula: string;
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  province_name: string;
  city_name: string;
  address: string;
  subtotal: string;
  shipping_fee: string;
  total: string;
  payment_method: "bank_transfer" | "whatsapp";
  payment_state: "pending" | "confirmed" | "stock_issue";
  paid_at: string | null;
  guide_number: string;
  tracking_number: string;
  status_id: string;
  status: OrderStatus;
  items: OrderLine[];
  history: OrderHistory[];
  receipts: { id: string; url: string; created_at: string }[];
}
export interface OrderTransitionRow {
  id: string;
  from_status_id: string;
  to_status_id: string;
  active: boolean;
  version: number;
}
export interface MediaAsset {
  id: string;
  url: string;
  name: string;
  width: number;
  height: number;
  size_bytes: number;
  created_at: string;
  version: number;
}
export interface OptionRow {
  id: string;
  slug: string;
  name_es: string;
  name_en: string;
  active: boolean;
  version: number;
  kind?: Variant["kind"];
  volume_ml?: string;
}
export interface AdminBrand {
  id: string;
  name: string;
  active: boolean;
  version: number;
  category_id: string;
}
