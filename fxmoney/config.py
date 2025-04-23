"""
Global settings for fxmoney:
- base_currency: the default base currency (e.g. EUR)
- fallback_mode: behavior when a rate is missing ("last" or "raise")
- request_timeout: HTTP timeout for REST backends
- precision: global Decimal precision and rounding
- currency_decimals: mapping ISO codes → minor-unit decimal places
"""

from dataclasses import dataclass, field
from decimal import getcontext, ROUND_HALF_EVEN


@dataclass
class _Settings:
    base_currency: str = "EUR"
    fallback_mode: str = "last"    # "last" → use last known rate, "raise" → error
    request_timeout: float = 3.0
    precision: int = 16            # internal Decimal precision
    rounding: str = ROUND_HALF_EVEN
    # number of decimal places per currency (minor units)
    currency_decimals: dict[str, int] = field(default_factory=lambda: {
        "EUR": 2, "USD": 2, "JPY": 0, "GBP": 2, "CHF": 2,
        "AUD": 2, "CAD": 2, "CNY": 2, "KRW": 0, "KWD": 3,
        # add more as needed...
    })

    def apply(self):
        """Apply global Decimal settings (precision & rounding)."""
        ctx = getcontext()
        ctx.prec = self.precision
        ctx.rounding = self.rounding


settings = _Settings()
settings.apply()


def set_base_currency(code: str):
    """Set the global base currency (ISO code)."""
    settings.base_currency = code.upper()


def set_fallback_mode(mode: str):
    """Set the fallback mode: 'last' or 'raise'."""
    assert mode in ("last", "raise")
    settings.fallback_mode = mode


def set_timeout(seconds: float):
    """Set the HTTP timeout for REST backends."""
    settings.request_timeout = float(seconds)


def set_currency_decimals(code: str, decimals: int):
    """Override the minor-unit mapping for a single currency."""
    settings.currency_decimals[code.upper()] = decimals


def set_all_currency_decimals(mapping: dict[str, int]):
    """Replace the entire currency_decimals mapping."""
    settings.currency_decimals = {k.upper(): v for k, v in mapping.items()}
