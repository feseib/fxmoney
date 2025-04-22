"""
ECB FX‑Rate Backend for fxmoney
Loads historical & current exchange rates from the ECB CSV and caches them locally.
"""

from __future__ import annotations
import csv
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
import requests

from .exceptions import MissingRateError
from ..config import settings

# ECB CSV URL and local cache path
CSV_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.csv"
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".fxmoney")
CACHE_FILE = os.path.join(CACHE_DIR, "eurofxref-hist.csv")
DATE_FMT = "%Y-%m-%d"


class ECBBackend:
    """FX backend using ECB historical rates via CSV download and cache."""

    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        if not self._is_cache_fresh():
            self._download_csv()
        self._rates = self._load_rates()

    def _is_cache_fresh(self) -> bool:
        """Check if the cache file is younger than 24 hours."""
        try:
            mtime = os.path.getmtime(CACHE_FILE)
            return (datetime.now().timestamp() - mtime) < 24 * 3600
        except OSError:
            return False

    def _download_csv(self):
        """Download the ECB CSV file to local cache."""
        resp = requests.get(CSV_URL, timeout=settings.request_timeout)
        resp.raise_for_status()
        with open(CACHE_FILE, "wb") as f:
            f.write(resp.content)

    def _load_rates(self) -> dict[date, dict[str, Decimal]]:
        """Parse the CSV into a dict mapping date → {currency: rate}."""
        rates: dict[date, dict[str, Decimal]] = {}
        with open(CACHE_FILE, encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            currencies = headers[1:]
            for row in reader:
                d = datetime.strptime(row[0], DATE_FMT).date()
                daily: dict[str, Decimal] = {}
                for cur, val in zip(currencies, row[1:]):
                    if val:
                        daily[cur] = Decimal(val)
                rates[d] = daily
        return rates

    def get_rate(self, src: str, tgt: str, on_date: date | None = None) -> float:
        """
        Get the rate from src to tgt on on_date.
        Falls back to the last available prior date if needed.
        """
        # choose date
        if on_date is None:
            on_date = max(self._rates.keys())

        # find the nearest date <= on_date
        available = [d for d in self._rates if d <= on_date]
        if not available:
            if settings.fallback_mode == "last":
                d0 = min(self._rates.keys())
            else:
                raise MissingRateError(f"No rates available on or before {on_date}")
        else:
            d0 = max(available)

        daily = self._rates[d0]

        # same currency
        if src == tgt:
            return 1.0

        # src → EUR
        if src == settings.base_currency:
            src_to_eur = Decimal(1)
        else:
            rate_src = daily.get(src)
            if rate_src is None:
                if settings.fallback_mode == "last":
                    return self.get_rate(src, tgt, d0 - timedelta(days=1))
                raise MissingRateError(f"No rate for {src} on {d0}")
            src_to_eur = Decimal(1) / rate_src

        # EUR → tgt
        if tgt == settings.base_currency:
            eur_to_tgt = Decimal(1)
        else:
            rate_tgt = daily.get(tgt)
            if rate_tgt is None:
                if settings.fallback_mode == "last":
                    return self.get_rate(src, tgt, d0 - timedelta(days=1))
                raise MissingRateError(f"No rate for {tgt} on {d0}")
            eur_to_tgt = rate_tgt

        return float(src_to_eur * eur_to_tgt)
