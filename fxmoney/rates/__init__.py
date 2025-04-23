"""
fxmoney – FX-Rate Backend Registry
Default backend: ECBBackend with historical ECB rates.
"""

from datetime import date
from decimal import Decimal
from typing import Protocol, runtime_checkable, Optional

from ..config import settings
from .exceptions import MissingRateError
from .ecb import ECBBackend

@runtime_checkable
class RateBackend(Protocol):
    def get_rate(
        self,
        src: str,
        tgt: str,
        on_date: Optional[date] = None
    ) -> float: ...

# install ECB by default
_current_backend: RateBackend = ECBBackend()

def install_backend(backend: RateBackend):
    """Switch the active FX-rate backend."""
    global _current_backend
    _current_backend = backend

def get_backend() -> RateBackend:
    """Return the active FX-rate backend."""
    return _current_backend

def convert_amount(
    amount: Decimal,
    src: str,
    tgt: str,
    on_date: Optional[date] = None
) -> Decimal:
    """Convert `amount` from `src` to `tgt` currency at given date."""
    try:
        rate = Decimal(str(_current_backend.get_rate(src, tgt, on_date)))
    except MissingRateError:
        if settings.fallback_mode == "last":
            rate = Decimal(1)
        else:
            raise
    return amount * rate
