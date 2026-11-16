import { afterEach, expect, spyOn, test } from "bun:test";
import {
  backendUrl,
  clientIp,
  serverGet,
  withClientIp,
} from "../../src/shared/http/server";

const original = process.env.TRUST_PROXY;
afterEach(() => {
  if (original === undefined) delete process.env.TRUST_PROXY;
  else process.env.TRUST_PROXY = original;
});

const request = (realIp?: string) =>
  new Request("http://localhost/", {
    headers: realIp ? { "X-Real-IP": realIp } : {},
  });

test("la IP de nginx solo se acepta con TRUST_PROXY", () => {
  delete process.env.TRUST_PROXY;
  expect(clientIp(request("203.0.113.5"), "127.0.0.1")).toBe("127.0.0.1");
  process.env.TRUST_PROXY = "true";
  expect(clientIp(request("203.0.113.5"), "172.18.0.2")).toBe("203.0.113.5");
  expect(clientIp(request("no es una ip"), "172.18.0.2")).toBe("172.18.0.2");
  expect(clientIp(request(), "")).toBe("");
});

test("el SSR reenvía la IP de la petición en curso al backend", async () => {
  const fetch = spyOn(globalThis, "fetch").mockRejectedValue(
    new Error("Unexpected fetch"),
  );
  fetch
    .mockResolvedValueOnce(Response.json({ data: {} }))
    .mockResolvedValueOnce(Response.json({ data: {} }));
  try {
    await withClientIp("198.51.100.4", () =>
      serverGet("/api/v1/catalog/facets"),
    );
    expect(
      new Headers(fetch.mock.calls.at(-1)?.[1]?.headers).get("x-real-ip"),
    ).toBe("198.51.100.4");
    await serverGet("/api/v1/catalog/facets");
    expect(
      new Headers(fetch.mock.calls.at(-1)?.[1]?.headers).get("x-real-ip"),
    ).toBeNull();
  } finally {
    fetch.mockRestore();
  }
});

test("el backend solo puede ser un origen HTTP interno fijo", () => {
  const original = process.env.BACKEND_URL;
  try {
    for (const valid of ["http://api:8000", "http://127.0.0.1:5000"]) {
      process.env.BACKEND_URL = valid;
      expect(backendUrl()).toBe(valid);
    }
    for (const invalid of [
      "https://api:8000",
      "http://evil.example",
      "http://user:pass@api:8000",
      "http://api:8000/path",
    ]) {
      process.env.BACKEND_URL = invalid;
      expect(() => backendUrl()).toThrow();
    }
  } finally {
    if (original === undefined) delete process.env.BACKEND_URL;
    else process.env.BACKEND_URL = original;
  }
});
