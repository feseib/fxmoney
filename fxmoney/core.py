"""
Money class for fxmoney:
- amount: Decimal
- currency: ISO-4217 code (string)
- operators +, -, *, /    (left operand's currency dominates)
- comparisons  ==, <, <=, >, >=  (automatic FX conversion)
- to(target, date=None)   convert currency, optional historical date
- to_dict()/from_dict()   minimal dict for JSON
"""

from __future__ import annotations
from decimal import Decimal
from datetime import date
from typing import Any

from .config import settings
from .rates import convert_amount  # placeholder until real backends installed


class Money:
    """Precise money amount with ISO currency code and auto FX conversion."""

    __slots__ = ("amount", "currency")

    def __init__(self, amount: Any, currency: str):
        self.amount = Decimal(str(amount))
        self.currency = currency.upper()

    # Internal helper to convert 'other' to this currency
    def _coerce_amount(self, other: Money, on_date: date | None = None) -> Decimal:
        if self.currency == other.currency:
            return other.amount
        return convert_amount(other.amount, other.currency, self.currency, on_date)

    # Arithmetic operators
    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount + self._coerce_amount(other), self.currency)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount - self._coerce_amount(other), self.currency)

    def __mul__(self, factor: int | float | Decimal) -> Money:
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __truediv__(self, divisor: int | float | Decimal) -> Money:
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    # Comparison operators (auto-convert)
    def _pair(self, other: Money) -> tuple[Decimal, Decimal]:
        a = self.amount
        b = self._coerce_amount(other)
        return a, b

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        a, b = self._pair(other)
        return a == b

    def __lt__(self, other: Money):  a, b = self._pair(other); return a < b
    def __le__(self, other: Money):  a, b = self._pair(other); return a <= b
    def __gt__(self, other: Money):  a, b = self._pair(other); return a > b
    def __ge__(self, other: Money):  a, b = self._pair(other); return a >= b

    # Currency conversion
    def to(self, target: str, on_date: date | None = None) -> Money:
        tgt = target.upper()
        if tgt == self.currency:
            return self
        new_amt = convert_amount(self.amount, self.currency, tgt, on_date)
        return Money(new_amt, tgt)

    # Representations & JSON helpers
    def __repr__(self):
        return f"Money({str(self.amount)}, '{self.currency}')"

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def to_dict(self) -> dict[str, str]:
        """Minimal dict for JSON serialization."""
        return {"amount": str(self.amount), "currency": self.currency}

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> Money:
        """Construct Money from dict."""
        return cls(d["amount"], d["currency"])
