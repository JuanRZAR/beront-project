import { test, expect, spyOn } from "bun:test";
import { proxy } from "../../src/shared/http/proxy";

test("una carga interrumpida devuelve un error controlado", async () => {
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.error(new Error("Interrupted"));
    },
  });
  const response = await proxy(
    new Request("http://localhost/api/v1/cart/quote", {
      method: "POST",
      body: stream,
    }),
    "v1/cart/quote",
  );
  expect(response.status).toBe(400);
  expect((await response.json()).error.code).toBe("BAD_REQUEST");
});

test("el proxy rechaza destinos y rutas fuera de su contrato", async () => {
  const fetch = spyOn(globalThis, "fetch").mockRejectedValue(
    new Error("Unexpected fetch"),
  );
  try {
    for (const path of [
      "//evil.example/api/v1/admin",
      "v1/catalog/../admin",
      "v1/catalog/%2e%2e/admin",
      "v1/catalog/\\admin",
      "unknown",
    ]) {
      expect(
        (await proxy(new Request("http://localhost/api/" + path), path)).status,
      ).toBe(404);
    }
    expect(
      (await proxy(new Request("http://localhost/media/x.svg"), "x.svg", true))
        .status,
    ).toBe(404);
    expect(fetch).not.toHaveBeenCalled();
  } finally {
    fetch.mockRestore();
  }
});
test("el proxy limita el cuerpo antes de contactar al backend", async () => {
  const fetch = spyOn(globalThis, "fetch").mockRejectedValue(
    new Error("Unexpected fetch"),
  );
  try {
    const response = await proxy(
      new Request("http://localhost/api/v1/cart/quote", {
        method: "POST",
        body: "x".repeat(65537),
      }),
      "v1/cart/quote",
    );
    expect(response.status).toBe(413);
    expect(fetch).not.toHaveBeenCalled();
  } finally {
    fetch.mockRestore();
  }
});
test("el proxy conserva cookies separadas y no sigue redirecciones", async () => {
  const headers = new Headers({ "Content-Type": "application/json" });
  headers.append("Set-Cookie", "first=one; Path=/; HttpOnly");
  headers.append("Set-Cookie", "second=two; Path=/; HttpOnly");
  const fetch = spyOn(globalThis, "fetch").mockResolvedValue(
    new Response('{"data":{}}', { headers }),
  );
  try {
    const response = await proxy(
      new Request("http://localhost/api/v1/auth/csrf"),
      "v1/auth/csrf",
    );
    expect(response.headers.getSetCookie()).toHaveLength(2);
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect(fetch.mock.calls[0]?.[1]).toMatchObject({ redirect: "manual" });
  } finally {
    fetch.mockRestore();
  }
});

test("checkout y comprobantes conservan CSRF y el destino fijo", async () => {
  const fetch = spyOn(globalThis, "fetch").mockRejectedValue(
    new Error("Unexpected fetch"),
  );
  try {
    for (const path of [
      "v1/checkout/quote",
      "v1/orders",
      "v1/orders/track",
      "v1/admin/media",
      "v1/admin/orders/example/receipts",
    ]) {
      const upload =
        path === "v1/orders" ||
        path === "v1/admin/media" ||
        path.endsWith("/receipts");
      fetch.mockResolvedValueOnce(Response.json({ data: {} }));
      const response = await proxy(
        new Request("http://localhost/api/" + path, {
          method: "POST",
          headers: {
            "Content-Type": upload
              ? "multipart/form-data; boundary=testing"
              : "application/json",
            "X-CSRFToken": "test-token",
            Origin: "http://localhost:4321",
          },
          body: upload ? "x".repeat(65537) : "{}",
        }),
        path,
      );
      expect(response.status).toBe(200);
      const call = fetch.mock.calls.at(-1);
      expect(new URL(String(call?.[0])).hostname).toBe("127.0.0.1");
      expect(new Headers(call?.[1]?.headers).get("X-CSRFToken")).toBe(
        "test-token",
      );
    }
  } finally {
    fetch.mockRestore();
  }
});

test("un pedido JSON mantiene el límite de 64 KiB", async () => {
  const fetch = spyOn(globalThis, "fetch").mockRejectedValue(
    new Error("Unexpected fetch"),
  );
  try {
    const response = await proxy(
      new Request("http://localhost/api/v1/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "x".repeat(65537),
      }),
      "v1/orders",
    );
    expect(response.status).toBe(413);
    expect(fetch).not.toHaveBeenCalled();
  } finally {
    fetch.mockRestore();
  }
});

test("el proxy envía la dirección del cliente y descarta la que envía el navegador", async () => {
  const fetch = spyOn(globalThis, "fetch").mockRejectedValue(
    new Error("Unexpected fetch"),
  );
  try {
    const request = () =>
      new Request("http://localhost/api/v1/orders/recovery", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Client-IP": "203.0.113.99",
        },
        body: "{}",
      });
    const sent = async (address: string) => {
      fetch.mockResolvedValueOnce(Response.json({ data: {} }));
      await proxy(request(), "v1/orders/recovery", false, address);
      return new Headers(fetch.mock.calls.at(-1)?.[1]?.headers).get(
        "x-client-ip",
      );
    };
    expect(await sent("198.51.100.7")).toBe("198.51.100.7");
    expect(await sent("")).toBeNull();
    expect(await sent("no es una dirección")).toBeNull();
  } finally {
    fetch.mockRestore();
  }
});
