# fxmoney/rates/ecb.py

"""
ECB FX-Rate Backend for fxmoney
Loads historical & current exchange rates exclusively via the ECB ZIP download,
then caches and parses the embedded CSV.
Thread-safe on-demand refresh.
"""

from __future__ import annotations
import csv
import io
import os
import threading
import zipfile
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
import requests

from .exceptions import MissingRateError
from ..config import settings

ZIP_URL    = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
CACHE_DIR  = os.path.join(os.path.expanduser("~"), ".fxmoney")
CACHE_ZIP  = os.path.join(CACHE_DIR, "eurofxref-hist.zip")
DATE_FMT   = "%Y-%m-%d"


class ECBBackend:
    """FX backend using the ECB ZIP file with thread-safe cache refresh."""

    _lock = threading.Lock()

    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        with ECBBackend._lock:
            if not self._is_cache_fresh():
                self._download_and_extract()
            self._rates = self._load_rates()

    def _is_cache_fresh(self) -> bool:
        """Cache fresh iff ZIP file is <24 h alt."""
        try:
            mtime = os.path.getmtime(CACHE_ZIP)
            return (datetime.now().timestamp() - mtime) < 24 * 3600
        except OSError:
            return False

    def _download_and_extract(self):
        """Fetch the ZIP and extract the CSV into memory."""
        resp = requests.get(ZIP_URL, timeout=settings.request_timeout)
        resp.raise_for_status()
        with open(CACHE_ZIP, "wb") as f:
            f.write(resp.content)
        # unzip in place (we only need in-memory CSV parsing)
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            name = next(n for n in z.namelist() if n.endswith(".csv"))
            with z.open(name) as zf, open(os.path.join(CACHE_DIR, name), "wb") as out:
                out.write(zf.read())

    def _load_rates(self) -> dict[date, dict[str, Decimal]]:
        """Parse the extracted CSV into date → {currency: rate}."""
        csv_path = os.path.join(CACHE_DIR, "eurofxref-hist.csv")
        rates: dict[date, dict[str, Decimal]] = {}
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            headers   = next(reader)
            currencies= headers[1:]
            for row in reader:
                try:
                    d = datetime.strptime(row[0], DATE_FMT).date()
                except Exception:
                    continue
                daily: dict[str, Decimal] = {}
                for cur, val in zip(currencies, row[1:]):
                    if not val:
                        continue
                    try:
                        daily[cur] = Decimal(val)
                    except InvalidOperation:
                        continue
                rates[d] = daily
        return rates

    def get_rate(self, src: str, tgt: str, on_date: date | None = None) -> float:
        """
        Get rate src→tgt on on_date, auto-refreshing the ZIP if stale.
        """
        if not self._is_cache_fresh():
            with ECBBackend._lock:
                if not self._is_cache_fresh():
                    self._download_and_extract()
                    self._rates = self._load_rates()

        # choose the effective date
        if on_date is None:
            on_date = max(self._rates.keys())

        available = [d for d in self._rates if d <= on_date]
        if not available:
            if settings.fallback_mode == "last":
                d0 = min(self._rates.keys())
            else:
                raise MissingRateError(f"No rates available on or before {on_date}")
        else:
            d0 = max(available)

        daily = self._rates[d0]
        if src == tgt:
            return 1.0

        # src→EUR
        if src == settings.base_currency:
            src_to_eur = Decimal(1)
        else:
            rate_src = daily.get(src)
            if rate_src is None:
                if settings.fallback_mode == "last":
                    return self.get_rate(src, tgt, d0 - timedelta(days=1))
                raise MissingRateError(f"No rate for {src} on {d0}")
            src_to_eur = Decimal(1) / rate_src

        # EUR→tgt
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
