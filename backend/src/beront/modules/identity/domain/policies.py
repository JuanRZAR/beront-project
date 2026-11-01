from datetime import timedelta

PERMISSIONS = frozenset(
    {
        "catalog:read_private",
        "catalog:write",
        "inventory:read",
        "inventory:adjust",
        "commerce:write",
        "orders:read",
        "orders:manage",
        "orders:approve_payment",
    }
)


def session_valid(session, now):
    return (
        session.revoked_at is None
        and now < session.expires_at
        and now - session.last_seen_at < timedelta(minutes=30)
    )


def validate_password(password):
    if not 14 <= len(password) <= 128:
        raise ValueError("La contraseña debe tener entre 14 y 128 caracteres.")
