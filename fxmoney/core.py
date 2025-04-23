"""
Money class for fxmoney:
- amount: Decimal
- currency: ISO-4217 code (string)
- operators +, -, *, /    (left operand's currency dominates)
- comparisons  ==, <, <=, >, >=  (automatic FX conversion)
- to(target, date=None, fallback=None)   convert currency, optional historical date,
                                         optional per-call fallback override
- per-currency quantization for presentation
- to_dict()/from_dict()   minimal dict for JSON
"""

from __future__ import annotations
from decimal import Decimal
from datetime import date
from typing import Any, Optional

from .config import settings
from .rates import convert_amount  # updated to accept per-call fallback


class Money:
    """Precise money amount with ISO currency code, auto-FX conversion,
    and per-currency quantization for presentation."""

    __slots__ = ("amount", "currency")

    def __init__(self, amount: Any, currency: str):
        self.amount = Decimal(str(amount))
        self.currency = currency.upper()

    # ----- internal helpers -------------------------------------------------
    def _coerce_amount(
        self,
        other: Money,
        on_date: Optional[date] = None,
        fallback: Optional[str] = None
    ) -> Decimal:
        """Convert other's amount into this currency (raw Decimal)."""
        if self.currency == other.currency:
            return other.amount
        return convert_amount(other.amount, other.currency, self.currency, on_date, fallback)

    def _quantize(self, amt: Decimal) -> Decimal:
        """Quantize amt to minor units for this currency."""
        places = settings.currency_decimals.get(self.currency, 2)
        factor = Decimal(1).scaleb(-places)
        return amt.quantize(factor)

    # ----- arithmetic -------------------------------------------------------
    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        raw = self.amount + self._coerce_amount(other)
        return Money(raw, self.currency)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        raw = self.amount - self._coerce_amount(other)
        return Money(raw, self.currency)

    def __mul__(self, factor: int | float | Decimal) -> Money:
        raw = self.amount * Decimal(str(factor))
        return Money(raw, self.currency)

    def __truediv__(self, divisor: int | float | Decimal) -> Money:
        raw = self.amount / Decimal(str(divisor))
        return Money(raw, self.currency)

    # ----- comparison -------------------------------------------------------
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

    # ----- conversion -------------------------------------------------------
    def to(
        self,
        target: str,
        on_date: Optional[date] = None,
        fallback: Optional[str] = None
    ) -> Money:
        """
        Convert to target currency (ISO code).
        `on_date` for historical rate; `fallback` overrides global setting.
        """
        tgt = target.upper()
        if tgt == self.currency:
            return Money(self.amount, self.currency)
        raw = convert_amount(self.amount, self.currency, tgt, on_date, fallback)
        return Money(raw, tgt)

    # ----- representation & JSON helpers ----------------------------------
    def __repr__(self) -> str:
        return f"Money({str(self.amount)}, '{self.currency}')"

    def __str__(self) -> str:
        q = self._quantize(self.amount)
        return f"{q} {self.currency}"

    def to_dict(self) -> dict[str, str]:
        """Minimal dict for JSON serialization (quantized)."""
        q = self._quantize(self.amount)
        return {"amount": str(q), "currency": self.currency}

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> Money:
        """Construct Money from dict."""
        return cls(d["amount"], d["currency"])
