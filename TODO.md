# fxmoney – Roadmap

## v0.1.x (MVP)
- [x] Money-Kernklasse mit Decimal, Operatoren, Vergleich
- [x] Dummy-Backend als Platzhalter
- [x] Konfigurationsobjekt (Basis, Fallback, Timeout)
- [ ] EZB-Backend (CSV-Download, Cache, historisch)
- [ ] Austauschbarer REST-Backend (exchangerate.host)

## v0.2.x
- [ ] Pro-Währungs-Quantisierung (EUR=2, JPY=0 …)
- [ ] Fallback-Strategie via Settings und pro Aufruf
- [ ] Pydantic v2 TypeAdapter registrieren
- [ ] Threadsafe Kurs-Cache

## v0.3.x
- [ ] CLI-Tool: `fxmoney convert 100 USD EUR --date 2020-01-01`
- [ ] Async Hintergrund-Update (optional)

## v1.0
- [ ] Vollständige Testsuite
- [ ] PyPI-Release, README, Badge, Lizenz
