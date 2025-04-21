"""
Globale Einstellungen für fxmoney:
• Basiswährung (default EUR)
• Fallback-Modus bei fehlendem Kurs
• HTTP-Timeout (für REST-Backends)
• Globale Decimal-Präzision und Rundung
"""

from dataclasses import dataclass
from decimal import getcontext, ROUND_HALF_UP


@dataclass
class _Settings:
    # --- FX / Währungs­bezogen ---------------------------------------------
    base_currency: str = "EUR"          # Basiswährung, an der sich Backends orientieren
    fallback_mode: str = "last"         # "last"  -> letzter bekannter Kurs
                                         # "raise" -> MissingRateError auslösen
    # --- Netzwerk -----------------------------------------------------------
    request_timeout: float = 3.0        # Sekunden-Timeout für HTTP-Backend
    # --- Decimal ------------------------------------------------------------
    precision: int = 16                 # globale Decimal-Präzision (signifikante Stellen)

    # -----------------------------------------------------------------------
    def apply(self):
        """Globale Decimal-Konfiguration anwenden (einmal beim Import)."""
        ctx = getcontext()
        ctx.prec = self.precision
        ctx.rounding = ROUND_HALF_UP


# Singleton-Instanz mit Standardeinstellungen
settings = _Settings()
settings.apply()

# Convenience-Setter ---------------------------------------------------------
def set_base_currency(code: str):
    settings.base_currency = code.upper()

def set_fallback_mode(mode: str):
    assert mode in ("last", "raise")
    settings.fallback_mode = mode

def set_timeout(seconds: float):
    settings.request_timeout = float(seconds)
