import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from beront.shared.domain.errors import Conflict, DomainError, NotFound

FUNCTIONS = frozenset(
    {
        "commerce_bank_add",
        "commerce_bank_get",
        "commerce_bank_list",
        "commerce_bank_save",
        "commerce_city_add",
        "commerce_city_get",
        "commerce_city_list",
        "commerce_city_save",
        "commerce_destination",
        "commerce_province_add",
        "commerce_province_get",
        "commerce_province_list",
        "commerce_province_save",
        "commerce_settings_get",
        "commerce_settings_save",
        "orders_add",
        "orders_get",
        "orders_history_add",
        "orders_list",
        "orders_operation_lock",
        "orders_receipt_add",
        "orders_recovery_request",
        "orders_save",
        "orders_status_add",
        "orders_status_get",
        "orders_status_list",
        "orders_status_save",
        "orders_transition_add",
        "orders_transition_get",
        "orders_transition_list",
        "orders_transition_save",
        "media_get",
        "media_register",
        "media_list",
        "media_update",
        "media_delete",
        "media_visible",
        "audit_record",
        "identity_admin_get",
        "identity_admin_create",
        "identity_password_set",
        "identity_session_get",
        "identity_session_add",
        "identity_session_touch",
        "identity_session_revoke",
        "identity_sessions_revoke_all",
        "catalog_product_get",
        "catalog_category_list",
        "catalog_category_get",
        "catalog_category_add",
        "catalog_category_save",
        "catalog_audience_list",
        "catalog_audience_get",
        "catalog_audience_add",
        "catalog_audience_save",
        "catalog_presentation_list",
        "catalog_presentation_get",
        "catalog_presentation_add",
        "catalog_presentation_save",
        "catalog_product_by_slug",
        "catalog_option_list",
        "catalog_option_get",
        "catalog_option_add",
        "catalog_option_save",
        "catalog_product_options_set",
        "catalog_candidates",
        "catalog_product_add",
        "catalog_product_save",
        "catalog_variant_get",
        "catalog_variant_add",
        "catalog_variant_save",
        "catalog_brands",
        "catalog_brand_get",
        "catalog_brand_add",
        "catalog_brand_save",
        "catalog_image_get",
        "catalog_image_by_filename",
        "catalog_image_add",
        "catalog_image_save",
        "catalog_image_delete",
        "inventory_ensure_decants",
        "inventory_ensure_bottles",
        "inventory_amounts",
        "inventory_balance_get",
        "inventory_balance_save",
        "inventory_movement_get",
        "inventory_movement_add",
        "inventory_balances",
        "inventory_movements",
    }
)


def json_default(value):
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError("Unsupported SQL parameter type")


def encode_payload(value):
    return json.dumps(value, default=json_default, allow_nan=False)


class PgCall:
    def __init__(self, connection):
        self.connection = connection

    def call(self, function, payload=None):
        if function not in FUNCTIONS:
            raise ValueError("SQL function is not registered")
        query = sql.SQL("SELECT {}.{}(%s) AS result").format(
            sql.Identifier("beront_api"), sql.Identifier(function)
        )
        try:
            row = self.connection.execute(
                query, [Jsonb(payload or {}, dumps=encode_payload)]
            ).fetchone()
            return row["result"]
        except psycopg.errors.RaiseException as error:
            code = error.diag.message_primary
            if code == "NOT_FOUND":
                raise NotFound() from error
            if code in {"VERSION_CONFLICT", "ADMIN_ALREADY_EXISTS"}:
                message = (
                    "Ya existe el ÃƒÂºnico administrador."
                    if code == "ADMIN_ALREADY_EXISTS"
                    else "El registro ha cambiado. Recarga los datos."
                )
                raise Conflict(code, message) from error
            if code == "PRODUCT_NOT_READY":
                raise DomainError(
                    code, "Un perfume publicado necesita una presentaciÃƒÂ³n activa."
                ) from error
            if code == "INVALID_OPTION":
                raise DomainError(
                    code, "Selecciona opciones de clasificación existentes y activas."
                ) from error
            if code == "INVALID_ADJUSTMENT":
                raise DomainError(code, "Las botellas se ajustan por unidades enteras.") from error
            if code == "ASSET_IN_USE":
                raise Conflict(code, "La fotografÃƒÂ­a estÃƒÂ¡ vinculada a un perfume.") from error
            if code == "INVALID_ASSET":
                raise DomainError(
                    code, "Selecciona una fotografÃƒÂ­a vÃƒÂ¡lida de la biblioteca."
                ) from error
            if code == "INVALID_PRESENTATION":
                raise DomainError(
                    code, "Configura y activa esta presentaciÃƒÂ³n antes de asignarla."
                ) from error
            if code == "DEFINITION_IN_USE":
                raise Conflict(
                    code,
                    "Retira esta presentaciÃƒÂ³n de los perfumes publicados antes de desactivarla.",
                ) from error
            if code in {"QUOTE_CHANGED", "INSUFFICIENT_STOCK", "BANK_UNAVAILABLE"}:
                raise Conflict(
                    code, "Los datos de compra han cambiado; revisa el carrito y el destino."
                ) from error
            if code == "CHECKOUT_NOT_CONFIGURED":
                raise DomainError(
                    code, "El propietario debe completar la configuración de compra."
                ) from error
            raise
        except psycopg.errors.UniqueViolation as error:
            if error.diag.constraint_name == "uq_administrators_singleton_slot":
                raise Conflict(
                    "ADMIN_ALREADY_EXISTS", "Ya existe el ÃƒÂºnico administrador."
                ) from error
            raise Conflict(
                "DATA_CONFLICT", "El cambio entra en conflicto con los datos existentes."
            ) from error


def require_record(value):
    if value is None:
        raise NotFound()
    return value
