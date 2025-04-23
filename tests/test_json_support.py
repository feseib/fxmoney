# tests/test_json_support.py

import pytest
pytest.importorskip("pydantic")

from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from fxmoney import Money, install_backend
from fxmoney.rates.ecb import ECBBackend


class ModelWithMoney(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    value: Money


def test_json_roundtrip():
    install_backend(ECBBackend())

    original = ModelWithMoney(value=Money("100.1234", "EUR"))
    json_str = original.model_dump_json()

    assert '"amount":"100.12"' in json_str
    assert '"currency":"EUR"' in json_str

    restored = ModelWithMoney.model_validate_json(json_str)
    assert isinstance(restored.value, Money)
    assert restored.value == Money("100.12", "EUR")   # quantised


def test_other_currency():
    install_backend(ECBBackend())
    original = ModelWithMoney(value=Money("1", "USD"))
    json_str = original.model_dump_json()
    restored = ModelWithMoney.model_validate_json(json_str)

    assert restored.value.currency == "USD"
    assert restored.value.amount == Decimal("1")
