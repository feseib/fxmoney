[![PyPI](https://img.shields.io/pypi/v/fxmoney)](https://pypi.org/project/fxmoney/)
[![Tests](https://github.com/<user>/fxmoney/actions/workflows/test.yml/badge.svg)](https://github.com/feseib/fxmoney/actions)


# fxmoney

Lightweight Python library for precise money arithmetic with pluggable FX-rate backends, automatic currency conversion, and clean JSON serialization.

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

- Decimal-based precision  
- Operator overloads for `+`, `-`, `*`, `/`  
- Automatic currency conversion with historical and live rates  
- Configurable fallback strategies  
- Clean, human-editable JSON serialization  
- Pluggable backends: ECB ZIP and exchangerate.host REST API  

## CLI Usage

```bash
fxmoney convert 100 USD EUR
fxmoney convert 100 USD EUR --date 2020-01-01 --fallback raise
fxmoney convert 100 USD EUR --verbose
```

## Background Update

### Thread-based
Enable automatic rate refresh every 4 hours:

```python
from fxmoney.updater import enable_background_update, disable_background_update

# Start background updater (runs every 4 hours)
enable_background_update()

# ... your application runs ...

# Stop background updater
disable_background_update()
```

### AsyncIO-based
Start an async task in your event loop:

```python
import asyncio
from fxmoney.updater import async_background_update

stop_evt = asyncio.Event()

# Schedule updater to run every 14400 seconds (4 hours)
asyncio.create_task(async_background_update(14400, stop_evt))

# ... your async application runs ...

# Signal the updater to stop
stop_evt.set()
```

## License

MIT License
