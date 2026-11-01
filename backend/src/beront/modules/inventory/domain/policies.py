from decimal import Decimal

from beront.shared.domain.errors import DomainError


class DecantStockPolicy:
    @staticmethod
    def required(volume_ml: Decimal, quantity: int) -> Decimal:
        return volume_ml * quantity


class BottleStockPolicy:
    @staticmethod
    def required(volume_ml: Decimal, quantity: int) -> Decimal:
        return Decimal(quantity)


def adjusted_balance(kind, current, delta):
    if not delta.is_finite() or delta == 0 or delta.as_tuple().exponent < -2:
        raise DomainError(
            "INVALID_ADJUSTMENT", "El ajuste debe ser un decimal no nulo de hasta dos decimales."
        )
    if kind == "full_bottle" and delta != delta.to_integral_value():
        raise DomainError("INVALID_ADJUSTMENT", "Las botellas se ajustan por unidades enteras.")
    result = current + delta
    limit = Decimal("2147483647") if kind == "full_bottle" else Decimal("9999999999.99")
    if result < 0:
        raise DomainError("NEGATIVE_STOCK", "El ajuste no puede dejar existencias negativas.")
    if result > limit:
        raise DomainError("INVALID_ADJUSTMENT", "El saldo excede el límite permitido.")
    return result
