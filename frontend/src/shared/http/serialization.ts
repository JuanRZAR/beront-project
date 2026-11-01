export function safeJson(value: unknown) {
  return JSON.stringify(value)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026")
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");
}
export function mediaUrl(value: string) {
  return /^\/media\/[a-f0-9]{32}\.webp$/.test(value) ? value : "";
}
