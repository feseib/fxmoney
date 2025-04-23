import pytest
from decimal import Decimal
from fxmoney.core import Money
from fxmoney.config import set_currency_decimals, set_all_currency_decimals, settings

def test_quantization_eur_default():
    m = Money("123.4567", "EUR")
    # EUR has 2 decimal places by default
    assert str(m) == "123.46 EUR"
    assert m.to_dict() == {"amount": "123.46", "currency": "EUR"}

def test_quantization_jpy_default():
    m = Money("123.4567", "JPY")
    # JPY has 0 decimal places by default
    assert str(m) == "123 JPY"
    assert m.to_dict() == {"amount": "123", "currency": "JPY"}

def test_quantization_kwd_default():
    m = Money("1.23456", "KWD")
    # KWD has 3 decimal places by default
    assert str(m) == "1.235 KWD"
    assert m.to_dict() == {"amount": "1.235", "currency": "KWD"}

def test_override_currency_decimals():
    # temporarily override EUR to 3 decimals
    set_currency_decimals("EUR", 3)
    m = Money("123.4567", "EUR")
    assert str(m) == "123.457 EUR"
    assert m.to_dict() == {"amount": "123.457", "currency": "EUR"}
    # reset to defaults
    set_all_currency_decimals({
        **settings.currency_decimals,
        "EUR": 2
    })
