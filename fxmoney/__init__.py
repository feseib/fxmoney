"""
fxmoney – precise money arithmetic with on-demand FX conversion.
Version 0.1.0-alpha
"""

from .config import settings, set_base_currency, set_fallback_mode, set_timeout
from .core import Money
from .rates import install_backend, get_backend

# Register Pydantic support if available
try:
    import fxmoney.json_support  # noqa: F401
except ImportError:
    pass

__all__ = [
    "Money",
    "settings",
    "set_base_currency",
    "set_fallback_mode",
    "set_timeout",
    "install_backend",
    "get_backend",
]
