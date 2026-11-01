from datetime import UTC, datetime, timedelta
from decimal import Decimal
from io import BytesIO
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pytest
from PIL import Image

from beront.modules.cart.domain.entities import CartQuote, QuoteLine
from beront.modules.cart.domain.policies import consolidate_items
from beront.modules.cart.infrastructure.whatsapp import WhatsAppLinkBuilder
from beront.modules.catalog.domain.entities import Product, Variant
from beront.modules.catalog.domain.policies import ensure_publishable, ensure_version
from beront.modules.catalog.infrastructure.images import LocalImageStorage
from beront.modules.identity.domain.entities import AdminSession
from beront.modules.identity.domain.policies import session_valid, validate_password
from beront.modules.inventory.application.availability import StockAvailability
from beront.modules.inventory.application.contracts import StockRequirement
from beront.modules.inventory.domain.policies import (
    BottleStockPolicy,
    DecantStockPolicy,
    adjusted_balance,
)
from beront.shared.domain.errors import Conflict, DomainError, NotFound
from beront.shared.domain.values import decimal_text, decimal_value


@pytest.mark.parametrize("value", ["NaN", "Infinity", "0.001", "10000000000", "not-money"])
def test_bad_decimals(value):
    with pytest.raises(ValueError):
        decimal_value(value)


def test_money_is_exact():
    assert decimal_text(decimal_value("0.10") + decimal_value("0.20")) == "0.30"
    assert decimal_value(3) == Decimal("3.00")
    with pytest.raises(ValueError):
        decimal_value("0", positive=True)


def test_cart_duplicates_and_limits():
    identifier = uuid4()
    assert consolidate_items(
        [{"variant_id": identifier, "quantity": 2}, {"variant_id": identifier, "quantity": 3}]
    ) == {identifier: 5}
    for items in (
        [],
        [{"variant_id": identifier, "quantity": 21}],
        [{"variant_id": uuid4(), "quantity": 1} for _ in range(21)],
        [{"variant_id": identifier, "quantity": 11}] * 2,
    ):
        with pytest.raises(DomainError):
            consolidate_items(items)


@pytest.mark.parametrize("quantity", [0, -1, 0.5, True, "2"])
def test_cart_bad_quantities(quantity):
    with pytest.raises(DomainError):
        consolidate_items([{"variant_id": uuid4(), "quantity": quantity}])


@pytest.mark.parametrize(
    "kind,current,delta",
    [
        ("decant", "1", "-2"),
        ("decant", "1", "0"),
        ("decant", "1", "0.001"),
        ("decant", "9999999999", "1"),
        ("full_bottle", "2", "0.5"),
        ("full_bottle", "2147483647", "1"),
        ("decant", "0", "NaN"),
    ],
)
def test_invalid_stock_changes(kind, current, delta):
    with pytest.raises(DomainError):
        adjusted_balance(kind, Decimal(current), Decimal(delta))


def test_stock_strategies():
    assert DecantStockPolicy.required(Decimal("7.50"), 2) == Decimal("15")
    assert BottleStockPolicy.required(Decimal("100"), 2) == Decimal("2")
    assert adjusted_balance("decant", Decimal("20"), Decimal("-10.50")) == Decimal("9.50")


def test_shared_inventory_and_independent_bottles():
    product, first, second, bottle = uuid4(), uuid4(), uuid4(), uuid4()

    class Repository:
        def amounts(self, kind, targets):
            return {product: Decimal("15")} if kind == "decant" else {bottle: Decimal("1")}

    requirements = [
        StockRequirement(product, first, "decant", Decimal("5"), 2),
        StockRequirement(product, second, "decant", Decimal("10"), 1),
        StockRequirement(product, bottle, "full_bottle", Decimal("100"), 1),
    ]
    service = StockAvailability(Repository())
    assert all(service.inspect(requirements).values())
    assert service.inspect(requirements, aggregate=True) == {
        first: False,
        second: False,
        bottle: True,
    }


def test_session_deadlines():
    now = datetime.now(UTC)
    record = AdminSession(uuid4(), uuid4(), "hash", now, now, now + timedelta(hours=8))
    assert session_valid(record, now)
    assert not session_valid(record, now + timedelta(minutes=30))
    record.last_seen_at = now + timedelta(hours=7, minutes=59)
    assert not session_valid(record, now + timedelta(hours=8))
    record.revoked_at = now
    assert not session_valid(record, now)


def test_password_length_and_version():
    validate_password("a sufficiently long password")
    for password in ("short", "x" * 129):
        with pytest.raises(ValueError):
            validate_password(password)
    product = Product(uuid4(), uuid4(), "Test", "test", "unisex", [], published=True)
    with pytest.raises(DomainError):
        ensure_publishable(product)
    product.variants = [Variant(uuid4(), product.id, "decant", Decimal("7.5"), Decimal("3"))]
    ensure_publishable(product)
    ensure_version(product, 1)
    with pytest.raises(Conflict):
        ensure_version(product, 2)


@pytest.mark.parametrize("locale", ["es", "en"])
def test_whatsapp_encoding_and_missing_configuration(locale):
    lines = [
        QuoteLine(
            uuid4(),
            "Casa & prueba",
            "Ámbar / claro",
            "full_bottle",
            Decimal("100"),
            2,
            Decimal("0.10"),
        )
    ]
    link = WhatsAppLinkBuilder("00000000").build(lines, locale)
    parsed = urlparse(link)
    text = parse_qs(parsed.query)["text"][0]
    assert "Ámbar / claro" in text and "USD 0.20" in text
    assert parsed.netloc == "wa.me"
    assert WhatsAppLinkBuilder("").build(lines, locale) is None
    assert CartQuote(lines, link).total == Decimal("0.20")


def test_image_normalization(tmp_path):
    store = LocalImageStorage(tmp_path)
    source = BytesIO()
    Image.new("RGB", (10, 20), "#B8A58A").save(source, "PNG")
    source.seek(0)
    name = store.save(source)
    with Image.open(store.path(name)) as image:
        assert image.format == "WEBP"
        assert not image.getexif()
    store.delete(name)
    assert not store.path(name).exists()
    assert not list(store.staging.iterdir())
    with pytest.raises(NotFound):
        store.path("../secret")
    with pytest.raises(DomainError):
        store.save(BytesIO(b"<svg></svg>"))
    with pytest.raises(DomainError):
        store.save(BytesIO(b"x" * (5 * 1024 * 1024 + 1)))
    animated = BytesIO()
    Image.new("RGB", (2, 2)).save(animated, "GIF")
    animated.seek(0)
    with pytest.raises(DomainError):
        store.save(animated)
