import base64
import json

import pytest

from beront.modules.orders.domain.policies import sign_quote, verify_quote
from beront.shared.domain.errors import Conflict, DomainError


def test_signed_quote_preserves_unicode_and_rejects_changed_total_or_key():
    snapshot = {
        "total": "125.25",
        "terms_text": "Condición de revisión. " * 800,
        "items": [{"product_name": "Ámbar", "unit_price": "120.00"}],
    }
    key = "server-secret-for-test-only"
    token = sign_quote(snapshot, key)
    assert verify_quote(token, key) == snapshot
    with pytest.raises(Conflict):
        verify_quote(token, "another-test-key")
    _, signature = token.split(".")
    snapshot["total"] = "0.01"
    modified = base64.urlsafe_b64encode(json.dumps(snapshot).encode()).decode().rstrip("=")
    with pytest.raises(Conflict):
        verify_quote(modified + "." + signature, key)


def test_quote_size_is_rejected_before_issuing_unusable_form_token():
    with pytest.raises(DomainError, match="propietario"):
        sign_quote({"terms_text": "a" * 60000}, "test-key")
