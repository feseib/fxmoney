# tests/test_cli.py

import sys
import pytest
from fxmoney.cli import main

# Dummy rate function for predictable outputs
def dummy_get_rate(self, src: str, tgt: str, on_date=None) -> float:
    return 2.0

@pytest.fixture(autouse=True)
def stub_ecb_rate(monkeypatch):
    """
    Stub the ECBBackend.get_rate method so that all currency conversions
    use a fixed rate of 2.0, without replacing the class (Lock stays intact).
    """
    import fxmoney.rates.ecb as ecb_module
    monkeypatch.setattr(ecb_module.ECBBackend, "get_rate", dummy_get_rate)
    yield

def run_cli(args, monkeypatch, capsys):
    # Prepare sys.argv for the CLI
    monkeypatch.setattr(sys, "argv", ["fxmoney"] + args)
    main()
    # Capture stdout
    captured = capsys.readouterr()
    return captured.out

def test_cli_convert_default(monkeypatch, capsys):
    out = run_cli(["convert", "100", "EUR", "USD"], monkeypatch, capsys)
    # dummy rate=2.0 → 100 EUR → 200.00 USD
    assert out.strip() == "200.00 USD"

def test_cli_convert_verbose(monkeypatch, capsys):
    out = run_cli(
        ["convert", "100", "EUR", "USD", "--verbose"],
        monkeypatch,
        capsys
    )
    lines = out.strip().splitlines()
    assert lines[0] == "Rate (EUR→USD): 2.0"
    assert lines[1] == "Result: 200.00 USD"
