# fxmoney

Lightweight Python library for precise money arithmetic with pluggable FX‑rate backends, automatic currency conversion, and clean JSON serialization.

## Installation

```bash
pip install fxmoney
```

## Quickstart

```python
from fxmoney import Money, install_backend

# Use the default ECB backend
a = Money(2, "EUR")
b = Money(3, "USD")
total = a + b
print(total)             # prints the sum in EUR
print(total.to("GBP"))   # converts to GBP
```

## Features

- Decimal‑based precision  
- Operator overloads for `+`, `-`, `*`, `/`  
- Automatic currency conversion with historical and live rates  
- Configurable fallback strategies  
- Clean, human‑editable JSON serialization  
- Pluggable backends: ECB CSV and exchangerate.host REST API  

See the full documentation and examples on GitHub.

## License

MIT License
