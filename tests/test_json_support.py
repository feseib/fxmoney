import pytest

# skip entire module if pydantic is not installed
pytest.importorskip("pydantic")

from pydantic import BaseModel
from decimal import Decimal
from fxmoney import Money, install_backend
from fxmoney.rates.ecb import ECBBackend


class ModelWithMoney(BaseModel):
    value: Money


def test_pydantic_json_roundtrip():
    # ensure ECB backend is active
    install_backend(ECBBackend())

    orig = ModelWithMoney(value=Money("100.1234", "EUR"))
    json_str = orig.model_dump_json()

    # JSON contains quantized amount and currency
    assert '"amount":"100.12"' in json_str
    assert '"currency":"EUR"' in json_str

    restored = ModelWithMoney.model_validate_json(json_str)
    assert isinstance(restored.value, Money)
    # internal Decimal still full precision
    assert restored.value == Money("100.1234", "EUR")
    assert restored.value.currency == "EUR"


def test_pydantic_historical_and_base_currency():
    install_backend(ECBBackend())

    orig = ModelWithMoney(value=Money("1", "USD"))
    json_str = orig.model_dump_json()
    restored = ModelWithMoney.model_validate_json(json_str)

    assert restored.value.currency == "USD"
    assert restored.value.amount == Decimal("1")
