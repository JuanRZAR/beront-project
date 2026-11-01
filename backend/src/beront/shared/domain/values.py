from decimal import Decimal, InvalidOperation


def decimal_value(value, *, positive=False) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        result = Decimal("NaN")
    if not result.is_finite() or result.as_tuple().exponent < -2:
        raise ValueError("Se requiere un decimal finito con hasta dos decimales.")
    if abs(result) >= Decimal("10000000000") or (positive and result <= 0):
        raise ValueError("Valor fuera del rango permitido.")
    return result.quantize(Decimal("0.01"))


def decimal_text(value: Decimal) -> str:
    return format(value, ".2f")
