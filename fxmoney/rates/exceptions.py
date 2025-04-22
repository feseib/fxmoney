"""
fxmoney – FX‑Rate Backend Exceptions
"""

class MissingRateError(Exception):
    """
    Raised when no exchange rate is available for the requested currency/date
    and fallback_mode='raise' is set.
    """
    pass
