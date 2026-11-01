export function decimalUnits(value: string): bigint | null {
  const match = /^(-?)(\d{1,10})(?:\.(\d{1,2}))?$/.exec(value);
  if (!match) return null;
  const result =
    BigInt(match[2]!) * 100n + BigInt((match[3] ?? "").padEnd(2, "0"));
  return match[1] ? -result : result;
}
export function decimalString(value: bigint): string {
  const sign = value < 0n ? "-" : "",
    absolute = value < 0n ? -value : value;
  return (
    sign +
    String(absolute / 100n) +
    "." +
    String(absolute % 100n).padStart(2, "0")
  );
}
