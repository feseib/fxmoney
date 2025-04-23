import pytest
import requests
from datetime import date  # <-- hinzugefügt

from fxmoney.config import set_fallback_mode
from fxmoney.rates import get_backend, install_backend, convert_amount
from fxmoney.rates.ecb import ECBBackend
from fxmoney.rates.host import HostBackend
from fxmoney.rates.exceptions import MissingRateError

# --- ECB backend default --------------------------------------------------

def test_default_backend_is_ecb():
    # By default we should have ECBBackend installed
    backend = get_backend()
    assert isinstance(backend, ECBBackend)

# --- convert_amount uses active backend ------------------------------------

def test_convert_amount_raises_on_missing_rate_and_raise():
    install_backend(ECBBackend())
    set_fallback_mode("raise")
    # pick a date earlier than any in ECB history, e.g. year 1900
    with pytest.raises(MissingRateError):
        # this should raise because no rates exist that far back
        convert_amount(1, "EUR", "USD", date(1900, 1, 1))
    set_fallback_mode("last")

# --- HostBackend tests with monkeypatch ------------------------------------

class DummyResp:
    def __init__(self, rate):
        self._rate = rate
    def raise_for_status(self):
        pass
    def json(self):
        return {"info": {"rate": self._rate}}

@pytest.fixture(autouse=True)
def reset_fallback():
    # ensure fallback_mode reset after each test
    yield
    set_fallback_mode("last")

def test_host_backend_success(monkeypatch):
    set_fallback_mode("last")
    hb = HostBackend()
    # simulate a successful API response with rate=1.2345
    monkeypatch.setattr(requests, "get", lambda url, params, timeout: DummyResp(1.2345))
    rate = hb.get_rate("EUR", "USD")
    assert pytest.approx(rate, rel=1e-8) == 1.2345

def test_host_backend_fallback_last(monkeypatch):
    set_fallback_mode("last")
    hb = HostBackend()
    # simulate a network error
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(requests.RequestException()))
    # with fallback="last", error should be swallowed and 1.0 returned
    rate = hb.get_rate("EUR", "USD")
    assert rate == 1.0

def test_host_backend_fallback_raise(monkeypatch):
    set_fallback_mode("raise")
    hb = HostBackend()
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(requests.RequestException()))
    with pytest.raises(MissingRateError):
        hb.get_rate("EUR", "USD")
