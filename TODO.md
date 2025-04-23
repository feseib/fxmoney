# fxmoney – Roadmap

## v0.1.x (MVP)
- [x] Core Money class with Decimal, operators, comparisons
- [x] Dummy backend as placeholder
- [x] Configuration object (base currency, fallback mode, timeout)
- [x] ECB backend (ZIP download, cache, historical)
- [x] Pluggable REST backend (exchangerate.host)

## v0.2.x
- [x] Per-currency quantization (EUR=2, JPY=0, …)
- [x] Fallback strategy configurable globally and per-call
- [x] Pydantic v2 TypeAdapter registration for JSON
- [x] Thread-safe rate cache

## v0.3.x
- [x] CLI tool: `fxmoney convert 100 USD EUR --date 2020-01-01`
- [x] Async background update (optional)

## v1.0
- [ ] Complete test suite
- [ ] PyPI release, full README, badges, license
