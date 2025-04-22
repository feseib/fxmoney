"""
Global settings for fxmoney:
- base_currency: the default base currency (e.g. EUR)
- fallback_mode: behavior when a rate is missing ("last" or "raise")
- request_timeout: HTTP timeout for REST backends
- precision: global Decimal precision and rounding
"""

from dataclasses import dataclass
from decimal import getcontext, ROUND_HALF_UP


@dataclass
class _Settings:
    base_currency: str = "EUR"
    fallback_mode: str = "last"    # "last" → use last known rate, "raise" → error
    request_timeout: float = 3.0
    precision: int = 16

    def apply(self):
        """Apply global Decimal settings (precision & rounding)."""
        ctx = getcontext()
        ctx.prec = self.precision
        ctx.rounding = ROUND_HALF_UP


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
