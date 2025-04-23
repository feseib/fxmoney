"""
ExchangeRateHost FX-Rate Backend for fxmoney
Fetches live and historical rates via the exchangerate.host REST API.
"""

from __future__ import annotations
import requests
from datetime import date
from decimal import Decimal

from .exceptions import MissingRateError
from ..config import settings

API_URL = "https://api.exchangerate.host/convert"


class HostBackend:
    """Backend using exchangerate.host API for FX conversion."""

    def get_rate(self, src: str, tgt: str, on_date: date | None = None) -> float:
        params: dict[str, str] = {
            "from": src.upper(),
            "to": tgt.upper(),
            "amount": "1",
            "places": "6"
        }
        if on_date:
            params["date"] = on_date.isoformat()

        try:
            resp = requests.get(API_URL, params=params, timeout=settings.request_timeout)
            resp.raise_for_status()
            data = resp.json()
            rate = data.get("info", {}).get("rate")
            if rate is None:
                raise MissingRateError(f"No rate for {src}->{tgt} on {on_date}")
            return float(rate)

        except (requests.RequestException, ValueError) as e:
            # On failure, either fallback or raise MissingRateError
            if settings.fallback_mode == "last":
                return 1.0
            raise MissingRateError(f"Error fetching rate for {src}->{tgt} on {on_date}: {e}") from e
