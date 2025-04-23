import pytest
from fxmoney.core import Money
from decimal import Decimal
from datetime import date

def test_same_currency_add_sub():
    m1 = Money(10, "EUR")
    m2 = Money("5.5", "EUR")
    assert m1 + m2 == Money(Decimal("15.5"), "EUR")
    assert m1 - m2 == Money(Decimal("4.5"), "EUR")

def test_mul_div():
    m = Money("2.5", "USD")
    assert m * 2 == Money(Decimal("5.0"), "USD")
    assert m / 5 == Money(Decimal("0.5"), "USD")

def test_repr_str_and_dict_roundtrip():
    m = Money("7.00", "JPY")
    # repr is unaffected (amount stays '7.00' internally)
    assert repr(m) == "Money(7.00, 'JPY')"
    # str() now reflects quantization: JPY → 0 decimal places
    assert str(m) == "7 JPY"
    # round-trip via dict still works
    d = m.to_dict()
    m2 = Money.from_dict(d)
    assert m2 == m

def test_comparison_same_currency():
    a = Money("3.00", "CHF")
    b = Money("4.00", "CHF")
    assert a < b
    assert b > a
    assert a != b
    assert a == Money("3.00", "CHF")
