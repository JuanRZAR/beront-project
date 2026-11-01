import type { CartItem } from "../../shared/http/contracts";
const KEY = "beront.cart.v1";
const uuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
interface StorageLike {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}
export class CartStore {
  private items: CartItem[] | null = null;
  public persistent = true;
  constructor(private storage: StorageLike | null) {
    this.persistent = storage !== null;
  }
  read(): CartItem[] {
    if (this.items) return this.items.map((item) => ({ ...item }));
    let value: unknown;
    try {
      value = JSON.parse(this.storage?.getItem(KEY) ?? "[]");
    } catch {
      value = [];
      this.persistent = false;
    }
    const items = new Map<string, number>();
    if (Array.isArray(value))
      for (const entry of value) {
        if (
          !entry ||
          typeof entry !== "object" ||
          !uuid.test(entry.variant_id) ||
          !Number.isInteger(entry.quantity) ||
          entry.quantity < 1 ||
          entry.quantity > 20
        )
          continue;
        if (items.size >= 20 && !items.has(entry.variant_id)) continue;
        items.set(
          entry.variant_id,
          Math.min(20, (items.get(entry.variant_id) ?? 0) + entry.quantity),
        );
      }
    this.items = [...items].map(([variant_id, quantity]) => ({
      variant_id,
      quantity,
    }));
    return this.read();
  }
  private save(items: CartItem[]) {
    this.items = items;
    try {
      this.storage?.setItem(KEY, JSON.stringify(items));
    } catch {
      this.persistent = false;
    }
    if (typeof window !== "undefined")
      window.dispatchEvent(new Event("beront:cart"));
  }
  add(variant_id: string, quantity: number) {
    if (
      !uuid.test(variant_id) ||
      !Number.isInteger(quantity) ||
      quantity < 1 ||
      quantity > 20
    )
      throw new Error("CART_LIMIT");
    const items = this.read(),
      item = items.find((entry) => entry.variant_id === variant_id);
    if ((item?.quantity ?? 0) + quantity > 20 || (!item && items.length >= 20))
      throw new Error("CART_LIMIT");
    if (item) item.quantity += quantity;
    else items.push({ variant_id, quantity });
    this.save(items);
  }
  quantity(variant_id: string, quantity: number) {
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 20)
      throw new Error("CART_LIMIT");
    this.save(
      this.read().map((item) =>
        item.variant_id === variant_id ? { ...item, quantity } : item,
      ),
    );
  }
  remove(variant_id: string) {
    this.save(this.read().filter((item) => item.variant_id !== variant_id));
  }
  invalidate() {
    this.items = null;
  }
}
let storage: StorageLike | null = null;
try {
  if (typeof window !== "undefined") storage = window.localStorage;
} catch {}
export const cart = new CartStore(storage);
