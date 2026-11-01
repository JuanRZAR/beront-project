import hashlib
import hmac
import logging
import secrets
from datetime import UTC, datetime
from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from beront.modules.cart.domain.policies import consolidate_items
from beront.modules.catalog.application.query_catalog import CatalogQueryFacade
from beront.modules.inventory.domain.entities import Movement
from beront.modules.inventory.domain.policies import adjusted_balance
from beront.modules.orders.domain.policies import (
    RECOVERY_COOLDOWN_SECONDS,
    ensure_transition,
    fingerprint,
    sign_quote,
    verify_quote,
)
from beront.shared.domain.errors import Conflict, DomainError, NotFound


class OrderService:
    DEFINITIONS = frozenset({"statuses", "transitions"})

    def __init__(self, uow_factory, storage, quote_secret, mailer, frontend_origin=""):
        self.uow_factory, self.storage = uow_factory, storage
        self.quote_secret = quote_secret
        self.mailer, self.frontend_origin = mailer, frontend_origin.rstrip("/")

    def _quote(self, uow, data):
        quantities = consolidate_items(data["items"])
        selected, problems = CatalogQueryFacade.selection_in(uow, quantities)
        if problems:
            raise Conflict("INSUFFICIENT_STOCK", "La disponibilidad del carrito ha cambiado.")
        destination = uow.commerce.destination(data["city_id"])
        settings = uow.commerce.settings()
        if not settings or not settings["terms_" + data["locale"]]:
            raise DomainError(
                "CHECKOUT_NOT_CONFIGURED",
                "El propietario debe completar la configuración de compra.",
            )
        items = [
            {
                "variant_id": str(v.id),
                "product_id": str(p.id),
                "product_name": p.name,
                "brand_name": p.brand_name,
                "kind": v.kind,
                "volume_ml": f"{v.volume_ml:.2f}",
                "quantity": quantity,
                "unit_price": f"{v.price:.2f}",
                "line_total": f"{v.price * quantity:.2f}",
            }
            for p, v, quantity in selected
        ]
        items.sort(key=lambda row: row["variant_id"])
        subtotal = sum((Decimal(row["line_total"]) for row in items), Decimal("0.00"))
        fee = Decimal(destination["shipping_fee"])
        if subtotal + fee > Decimal("9999999999.99"):
            raise DomainError(
                "ORDER_TOTAL_LIMIT", "El total supera el importe admitido por el sistema."
            )
        result = {
            "currency": "USD",
            "items": items,
            "city_id": str(destination["id"]),
            "city_name": destination["name"],
            "province_name": destination["province_name"],
            "subtotal": f"{subtotal:.2f}",
            "shipping_fee": f"{fee:.2f}",
            "total": f"{subtotal + fee:.2f}",
            "terms_version": settings["version"],
            "locale": data["locale"],
            "terms_text": settings["terms_" + data["locale"]],
            "banks": uow.commerce.listing("banks"),
        }
        result["quote_token"] = sign_quote(result, self.quote_secret)
        return result, settings

    def quote(self, data):
        with self.uow_factory() as uow:
            return self._quote(uow, data)[0]

    def create(self, data, receipt_stream=None):
        filename = None
        committed = False
        asset_created = False
        try:
            receipt_data = None
            if data["payment_method"] == "bank_transfer":
                if receipt_stream is None:
                    raise DomainError("RECEIPT_REQUIRED", "Adjunta la fotografía del comprobante.")
                filename = self.storage.save(receipt_stream)
                receipt_data = self.storage.describe(filename)
            elif receipt_stream is not None:
                raise DomainError(
                    "UNEXPECTED_RECEIPT",
                    "El pago por WhatsApp no requiere adjuntar un comprobante aquí.",
                )
            request_hash = fingerprint(
                {"request": data, "receipt": receipt_data["checksum"] if receipt_data else None}
            )
            with self.uow_factory() as uow:
                uow.orders.lock_operation(data["operation_id"])
                existing = uow.orders.by_operation(data["operation_id"])
                if existing:
                    if existing["request_hash"] != request_hash:
                        raise Conflict(
                            "OPERATION_CONFLICT", "Esta operación ya se usó con otros datos."
                        )
                    return existing, False
                quote = verify_quote(data["quote_token"], self.quote_secret)
                expected_items = {
                    str(key): value for key, value in consolidate_items(data["items"]).items()
                }
                quoted_items = {row["variant_id"]: row["quantity"] for row in quote["items"]}
                if (
                    expected_items != quoted_items
                    or str(data["city_id"]) != quote["city_id"]
                    or data["locale"] != quote["locale"]
                ):
                    raise Conflict(
                        "QUOTE_CHANGED",
                        "Actualiza y revisa los importes antes de enviar el pedido.",
                    )
                settings = uow.commerce.settings()
                if data["payment_method"] == "whatsapp":
                    fresh, settings = self._quote(uow, data)
                    if fresh["quote_token"] != data["quote_token"]:
                        raise Conflict(
                            "QUOTE_CHANGED",
                            "Actualiza y revisa los importes antes de enviar el pedido.",
                        )
                if data["payment_method"] == "whatsapp" and not settings["whatsapp_number"]:
                    raise DomainError(
                        "WHATSAPP_NOT_CONFIGURED", "El propietario debe configurar su WhatsApp."
                    )
                bank = None
                if data["payment_method"] == "bank_transfer":
                    bank = next(
                        (row for row in quote["banks"] if row["id"] == str(data["bank_id"])), None
                    )
                    if not bank:
                        raise Conflict("BANK_UNAVAILABLE", "Selecciona una cuenta bancaria activa.")
                status = uow.orders.status(purpose=data["payment_method"])
                code = "BRT-" + secrets.token_urlsafe(18)
                order_id = uuid4()
                order = {
                    **quote,
                    **data["customer"],
                    "id": order_id,
                    "operation_id": data["operation_id"],
                    "request_hash": request_hash,
                    "code": code,
                    "code_hash": hashlib.sha256(code.encode()).hexdigest(),
                    "address": data["address"],
                    "payment_method": data["payment_method"],
                    "bank_snapshot": bank,
                    "terms_snapshot": {
                        "version": quote["terms_version"],
                        "locale": data["locale"],
                        "text": quote["terms_text"],
                    },
                    "status_id": status["id"],
                    "created_at": datetime.now(UTC),
                }
                uow.orders.add(order)
                uow.orders.history(order_id, status, None)
                if receipt_data:
                    asset, asset_created = uow.media.register(
                        {
                            **receipt_data,
                            "name": str(order_id),
                            "kind": "receipt",
                            "uploaded_by": None,
                        }
                    )
                    uow.orders.receipt(order_id, asset.id, None)
                uow.commit()
                committed = True
                return uow.orders.get(order_id), True
        finally:
            if filename and (not committed or not asset_created):
                self.storage.delete(filename)

    def track(self, code):
        with self.uow_factory() as uow:
            return uow.orders.by_code(hashlib.sha256(code.encode()).hexdigest())

    def get(self, identifier):
        with self.uow_factory() as uow:
            return uow.orders.get(identifier)

    def listing(self, query):
        with self.uow_factory() as uow:
            return uow.orders.listing(query)

    def approve_payment(self, identifier, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            order = uow.orders.get(identifier, lock=True)
            if order["paid_at"] is not None:
                return order, "already_confirmed"
            self._version(order, data["version"])
            if order["status"]["phase"] == "cancelled":
                raise Conflict("ORDER_CANCELLED", "El pedido está cancelado.")
            status = uow.orders.status(data["status_id"])
            if status["phase"] != "paid" or not status["active"]:
                raise Conflict("INVALID_TRANSITION", "Selecciona un estado de pago confirmado.")
            uow.orders.transition(order["status_id"], status["id"])
            products = {}
            for product_id in sorted({row["product_id"] for row in order["items"]}):
                products[product_id] = uow.catalog.product(UUID(product_id), lock=True)
            requirements = {}
            unavailable = False
            for line in order["items"]:
                key = (
                    line["kind"],
                    line["product_id"] if line["kind"] == "decant" else line["variant_id"],
                )
                amount = Decimal(line["quantity"]) * (
                    Decimal(line["volume_ml"]) if line["kind"] == "decant" else 1
                )
                requirements[key] = requirements.get(key, Decimal("0")) + amount
                product = products[line["product_id"]]
                variant = next(v for v in product.variants if str(v.id) == line["variant_id"])
                unavailable |= product.sold_out or variant.sold_out
            balances = {}
            for key, amount in sorted(requirements.items()):
                balance = uow.stock.balance(key[0], UUID(key[1]), lock=True)
                balances[key] = balance
                unavailable |= balance.amount < amount
            order["payment_verified_at"] = datetime.now(UTC)
            if unavailable:
                issue = uow.orders.status(purpose="stock_issue")
                if str(order["status_id"]) == str(issue["id"]):
                    return order, "stock_issue"
                uow.orders.transition(order["status_id"], issue["id"])
                order.update(status_id=issue["id"], payment_state="stock_issue")
                uow.orders.save(order)
                uow.orders.history(identifier, issue, actor_id)
                uow.audit(actor_id, "orders.payment_stock_issue", identifier, request_id)
                uow.commit()
                return uow.orders.get(identifier), "stock_issue"
            for key, amount in sorted(requirements.items()):
                balance = balances[key]
                balance.amount = adjusted_balance(key[0], balance.amount, -amount)
                uow.stock.save_balance(balance)
                operation_id = uuid5(NAMESPACE_URL, f"beront:order:{identifier}:{key}")
                movement = Movement(
                    uuid4(),
                    key[0],
                    UUID(key[1]),
                    -amount,
                    balance.amount,
                    balance.version,
                    "Pedido " + str(identifier),
                    actor_id,
                    operation_id,
                    fingerprint({"order": identifier, "target": key, "amount": amount}),
                    datetime.now(UTC),
                )
                uow.stock.add_movement(movement, balance.id)
            order.update(
                status_id=status["id"],
                payment_state="confirmed",
                paid_at=datetime.now(UTC),
                approved_by=actor_id,
            )
            uow.orders.save(order)
            uow.orders.history(identifier, status, actor_id)
            uow.audit(actor_id, "orders.payment_confirmed", identifier, request_id)
            uow.commit()
            return uow.orders.get(identifier), "confirmed"

    def transition(self, identifier, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            order = uow.orders.get(identifier, lock=True)
            self._version(order, data["version"])
            status = uow.orders.status(data["status_id"])
            uow.orders.transition(order["status_id"], status["id"])
            for field in ("guide_number", "tracking_number"):
                if field in data:
                    order[field] = data[field]
            ensure_transition(order, status)
            order["status_id"] = status["id"]
            uow.orders.save(order)
            uow.orders.history(identifier, status, actor_id)
            uow.audit(actor_id, "orders.transition", identifier, request_id)
            uow.commit()
            return uow.orders.get(identifier)

    def definitions(self, resource):
        if resource not in self.DEFINITIONS:
            raise NotFound()
        with self.uow_factory() as uow:
            return uow.orders.definitions(resource)

    def update_shipping(self, identifier, data, actor_id, request_id=None):
        with self.uow_factory() as uow:
            order = uow.orders.get(identifier, lock=True)
            self._version(order, data["version"])
            order.update(guide_number=data["guide_number"], tracking_number=data["tracking_number"])
            uow.orders.save(order)
            uow.audit(actor_id, "orders.shipping_update", identifier, request_id)
            uow.commit()
            return uow.orders.get(identifier)

    def create_definition(self, resource, data, actor_id, request_id=None):
        if resource not in self.DEFINITIONS:
            raise NotFound()
        with self.uow_factory() as uow:
            result = uow.orders.add_definition(resource, {"id": uuid4(), **data})
            uow.audit(actor_id, "orders." + resource + "_create", result["id"], request_id)
            uow.commit()
            return result

    def update_definition(self, resource, identifier, data, actor_id, request_id=None):
        if resource not in self.DEFINITIONS:
            raise NotFound()
        with self.uow_factory() as uow:
            result = uow.orders.save_definition(resource, identifier, data)
            uow.audit(actor_id, "orders." + resource + "_update", identifier, request_id)
            uow.commit()
            return result

    def recover(self, cedula, client_address):
        if not self.mailer.configured:
            raise DomainError(
                "RECOVERY_UNAVAILABLE", "La recuperación por correo no está disponible por ahora."
            )
        ip_hash = hmac.new(
            self.quote_secret.encode(), client_address.encode(), "sha256"
        ).hexdigest()
        with self.uow_factory() as uow:
            result = uow.orders.recover(cedula, ip_hash, RECOVERY_COOLDOWN_SECONDS)
            uow.commit()
        if not result["allowed"]:
            raise DomainError(
                "RECOVERY_COOLDOWN",
                "Espera antes de solicitar otro código.",
                [{"field": "retry_after", "seconds": result["retry_after"]}],
            )
        for recipient, locale, orders in self._recovery_groups(result["orders"]):
            subject, body = self._recovery_message(locale, orders)
            try:
                self.mailer.send(recipient, subject, body)
            except Exception as error:
                logging.getLogger("beront").error(
                    "orders.recovery_mail_failed", extra={"exception_type": type(error).__name__}
                )

    @staticmethod
    def _recovery_groups(orders):
        groups = {}
        for order in orders:
            entry = groups.setdefault(order["email"], (order["locale"], []))
            entry[1].append(order)
        return [(email, locale, rows) for email, (locale, rows) in groups.items()]

    def _recovery_message(self, locale, orders):
        english = locale == "en"
        lines = [
            ("Hello " if english else "Hola ") + orders[0]["first_name"] + ",",
            "",
            "These are the order codes registered with your identification number:"
            if english
            else "Estos son los códigos de pedido registrados con tu cédula:",
            "",
        ]
        lines += [f"{o['code']}  ({o['created_at'][:10]}, USD {o['total']})" for o in orders]
        if self.frontend_origin:
            lines += [
                "",
                ("Track your order: " if english else "Consulta tu pedido: ")
                + f"{self.frontend_origin}/{locale}/orders",
            ]
        lines += [
            "",
            "If you did not request this, you can ignore this message."
            if english
            else "Si no solicitaste este mensaje, puedes ignorarlo.",
        ]
        subject = "Your BÉRONT order code" if english else "Tu código de pedido BÉRONT"
        return subject, "\n".join(lines)

    def add_receipt(self, identifier, stream, actor_id, request_id=None):
        filename = self.storage.save(stream)
        keep = False
        try:
            with self.uow_factory() as uow:
                uow.orders.get(identifier, lock=True)
                asset, created = uow.media.register(
                    {
                        **self.storage.describe(filename),
                        "name": str(identifier),
                        "kind": "receipt",
                        "uploaded_by": actor_id,
                    }
                )
                uow.orders.receipt(identifier, asset.id, actor_id)
                uow.audit(actor_id, "orders.receipt_added", identifier, request_id)
                uow.commit()
                keep = created
                return uow.orders.get(identifier)
        finally:
            if not keep:
                self.storage.delete(filename)

    @staticmethod
    def _version(order, expected):
        if order["version"] != expected:
            raise Conflict()
