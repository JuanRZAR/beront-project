import { api, jsonRequest } from "../../shared/http/client";
import { bindForm } from "../../shared/http/forms";
import { errorMessage, showError } from "../../shared/http/errors";
import { translate, money, type Locale } from "../../shared/i18n";
import { byId, el, formatDate, setStatus } from "../../shared/components/dom";
import type {
  AdminOrder,
  OrderStatus,
  OrderTransitionRow,
} from "../../shared/http/contracts";

type Status = OrderStatus & { id: string; version: number };
const locale: Locale = document.documentElement.lang === "en" ? "en" : "es";
const t = translate(locale);
const PAGE_SIZE = 12;
const name = (row: { name_es: string; name_en: string }) =>
  locale === "en" ? row.name_en : row.name_es;
let statuses: Status[] = [];
let transitions: OrderTransitionRow[] = [];
let orders: AdminOrder[] = [];
let current: AdminOrder | null = null;
let page = 1;
let total = 0;
let query = "";
let filter = "";

const listError = byId("orders-error");
const message = (text: string) => setStatus("order-message", text);

function allowedTargets(order: AdminOrder) {
  const next = new Set(
    transitions
      .filter((row) => row.active && row.from_status_id === order.status_id)
      .map((row) => row.to_status_id),
  );
  return statuses.filter((row) => row.active && next.has(row.id));
}
function renderList() {
  byId("order-list").replaceChildren(
    ...orders.map((order) => {
      const li = el("li");
      const button = el("button", undefined, {
        type: "button",
        "aria-current": String(order.id === current?.id),
      });
      button.append(
        el("strong", order.code),
        el("small", `${order.first_name} ${order.last_name}`),
        el("small", `${name(order.status)} · ${money(order.total)}`),
      );
      button.addEventListener("click", () => void select(order.id));
      li.append(button);
      return li;
    }),
  );
  setStatus("orders-count", `${total} ${t("ordersFound")}`);
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  setStatus("orders-page", `${t("page")} ${page} / ${pages}`);
  byId<HTMLButtonElement>("orders-prev").disabled = page <= 1;
  byId<HTMLButtonElement>("orders-next").disabled = page >= pages;
}
async function loadList() {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(PAGE_SIZE),
  });
  if (query) params.set("q", query);
  if (filter) params.set("status_id", filter);
  try {
    const result = await api<AdminOrder[]>("/api/v1/admin/orders?" + params);
    orders = result.data;
    total = result.meta?.total ?? orders.length;
    listError.hidden = true;
    renderList();
  } catch (error) {
    showError(listError, error, locale);
  }
}
function line(order: AdminOrder) {
  return order.items.map((row) => {
    const li = el("li");
    const text = el("div");
    text.append(
      el("strong", row.product_name),
      el("small", row.brand_name),
      el(
        "small",
        `${row.kind === "decant" ? "Decant" : t("fullBottle")} ${Number(row.volume_ml)} ml · ${row.quantity}`,
      ),
    );
    li.append(text, el("span", money(row.line_total)));
    return li;
  });
}
function renderDetail(order: AdminOrder) {
  current = order;
  byId("order-placeholder").hidden = true;
  byId("order-detail").hidden = false;
  byId("detail-code").textContent = order.code;
  byId("detail-date").textContent = formatDate(order.created_at, locale);
  byId("detail-customer").textContent =
    `${order.first_name} ${order.last_name} · ${order.cedula}`;
  byId("detail-contact").textContent = `${order.phone} · ${order.email}`;
  byId("detail-delivery").textContent =
    `${order.province_name} · ${order.city_name}`;
  byId("detail-method").textContent =
    (order.address || t("agencyDelivery")) +
    " · " +
    (order.payment_method === "bank_transfer"
      ? t("bankTransfer")
      : t("payWhatsApp"));
  byId("detail-lines").replaceChildren(...line(order));
  byId("detail-subtotal").textContent = money(order.subtotal);
  byId("detail-shipping").textContent = money(order.shipping_fee);
  byId("detail-total").textContent = money(order.total);
  byId("detail-receipts").replaceChildren(
    ...(order.receipts.length
      ? order.receipts.map((row) =>
          el("img", undefined, {
            src: row.url,
            alt: t("receiptPreview"),
            loading: "lazy",
          }),
        )
      : [el("span", t("noReceipts"))]),
  );
  byId("detail-status").textContent = name(order.status);
  const phase = order.status.phase;
  const closed =
    order.paid_at !== null ||
    ["cancelled", "shipped", "delivered"].includes(phase);
  byId<HTMLButtonElement>("approve-payment").disabled = closed;
  byId<HTMLButtonElement>("cancel-order").disabled = closed;
  const next = byId<HTMLSelectElement>("next-status");
  const targets = allowedTargets(order).filter(
    (row) => !["paid", "stock_issue"].includes(row.phase),
  );
  next.replaceChildren(
    el("option", t("keepStatus"), { value: "" }),
    ...targets.map((row) => el("option", name(row), { value: row.id })),
  );
  const guide =
    byId("shipping-form").querySelector<HTMLInputElement>("[name=guide]")!;
  const tracking =
    byId("shipping-form").querySelector<HTMLInputElement>("[name=tracking]")!;
  guide.value = order.guide_number;
  tracking.value = order.tracking_number;
  syncShippingFields();
}
function syncShippingFields() {
  if (!current) return;
  const target = statuses.find(
    (row) => row.id === byId<HTMLSelectElement>("next-status").value,
  );
  const shipping =
    ["shipped", "delivered"].includes(target?.phase ?? "") ||
    ["shipped", "delivered"].includes(current.status.phase);
  for (const id of ["guide-field", "tracking-field"]) {
    const field = byId(id);
    field.hidden = !shipping;
    const input = field.querySelector("input")!;
    input.required =
      shipping && ["shipped", "delivered"].includes(target?.phase ?? "");
  }
}
async function select(id: string) {
  try {
    const result = await api<AdminOrder>("/api/v1/admin/orders/" + id);
    message("");
    renderDetail(result.data);
    renderList();
  } catch (error) {
    showError(listError, error, locale);
  }
}
async function refresh(id: string) {
  await loadList();
  await select(id);
}

byId("next-status").addEventListener("change", syncShippingFields);
byId("approve-payment").addEventListener("click", async () => {
  if (!current) return;
  const target = allowedTargets(current).find((row) => row.phase === "paid");
  if (!target) {
    message(t("noPaidStatus"));
    return;
  }
  try {
    const result = await api<AdminOrder>(
      "/api/v1/admin/orders/" + current.id + "/approve-payment",
      jsonRequest("POST", { version: current.version, status_id: target.id }),
    );
    const outcome = (result as unknown as { payment_result?: string })
      .payment_result;
    await refresh(current.id);
    message(
      outcome === "stock_issue"
        ? t("paymentStockIssue")
        : outcome === "already_confirmed"
          ? t("paymentAlready")
          : t("paymentConfirmed"),
    );
  } catch (error) {
    message(errorMessage(error, locale));
  }
});
byId("cancel-order").addEventListener("click", async () => {
  if (!current) return;
  const target = allowedTargets(current).find(
    (row) => row.phase === "cancelled",
  );
  if (!target) {
    message(t("noCancelStatus"));
    return;
  }
  try {
    await api(
      "/api/v1/admin/orders/" + current.id + "/transition",
      jsonRequest("POST", { version: current.version, status_id: target.id }),
    );
    await refresh(current.id);
    message(t("saved"));
  } catch (error) {
    message(errorMessage(error, locale));
  }
});
bindForm(
  byId<HTMLFormElement>("shipping-form"),
  async (values) => {
    if (!current) return;
    const status = String(values.get("status") ?? "");
    const guide = String(values.get("guide") ?? "").trim();
    const tracking = String(values.get("tracking") ?? "").trim();
    if (status)
      await api(
        "/api/v1/admin/orders/" + current.id + "/transition",
        jsonRequest("POST", {
          version: current.version,
          status_id: status,
          ...(guide ? { guide_number: guide } : {}),
          ...(tracking ? { tracking_number: tracking } : {}),
        }),
      );
    else if (guide && tracking)
      await api(
        "/api/v1/admin/orders/" + current.id + "/shipping",
        jsonRequest("PATCH", {
          version: current.version,
          guide_number: guide,
          tracking_number: tracking,
        }),
      );
    else return;
    await refresh(current.id);
    message(t("saved"));
  },
  locale,
);
byId<HTMLInputElement>("receipt-upload").addEventListener(
  "change",
  async (event) => {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !current) return;
    const data = new FormData();
    data.set("file", file);
    try {
      await api("/api/v1/admin/orders/" + current.id + "/receipts", {
        method: "POST",
        body: data,
      });
      await refresh(current.id);
      message(t("receiptAdded"));
    } catch (error) {
      message(errorMessage(error, locale));
    } finally {
      input.value = "";
    }
  },
);
let timer: number | undefined;
byId("order-search").addEventListener("input", (event) => {
  window.clearTimeout(timer);
  timer = window.setTimeout(() => {
    query = (event.target as HTMLInputElement).value.trim();
    page = 1;
    void loadList();
  }, 300);
});
byId("order-filter").addEventListener("change", (event) => {
  filter = (event.target as HTMLSelectElement).value;
  page = 1;
  void loadList();
});
byId("orders-prev").addEventListener("click", () => {
  page = Math.max(1, page - 1);
  void loadList();
});
byId("orders-next").addEventListener("click", () => {
  page += 1;
  void loadList();
});

async function start() {
  try {
    [statuses, transitions] = await Promise.all([
      api<Status[]>("/api/v1/admin/order-flow/statuses").then((r) => r.data),
      api<OrderTransitionRow[]>("/api/v1/admin/order-flow/transitions").then(
        (r) => r.data,
      ),
    ]);
  } catch (error) {
    showError(listError, error, locale);
    return;
  }
  byId("order-filter").replaceChildren(
    el("option", t("allStatuses"), { value: "" }),
    ...statuses.map((row) => el("option", name(row), { value: row.id })),
  );
  await loadList();
}
void start();
