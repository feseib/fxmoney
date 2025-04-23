# fxmoney/json_support.py
"""
Pydantic v2 integration for fxmoney.Money.

✓ accepts either a Money instance or a dict {'amount','currency'}
✓ serialises Money back to that dict
✓ works with pydantic-core ≥ 2.0 (tested on 2.33.1)
"""

from __future__ import annotations

try:
    from pydantic_core import core_schema
    from .core import Money
except ImportError:          # Pydantic not installed
    __all__: list[str] = []
else:

    # --- validator (dict → Money, Money passthrough) -------------------------
    def _parse_money(v):
        if isinstance(v, Money):
            return v
        if isinstance(v, dict) and {"amount", "currency"} <= v.keys():
            return Money.from_dict(v)
        raise ValueError("Value must be Money or dict with 'amount'+'currency'")

    # --- schema builder ------------------------------------------------------
    def _money_core_schema(
        cls: type[Money],
        handler: core_schema.GetCoreSchemaHandler,   # noqa: U100
    ) -> core_schema.CoreSchema:
        any_schema = core_schema.any_schema()
        return core_schema.no_info_after_validator_function(
            _parse_money,
            any_schema,
            # single-arg serializer required by pydantic-core 2.33
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda m: m.to_dict()
            ),
        )

    # wrapper tolerating 2- or 3-arg calls
    def __get_pydantic_core_schema__(cls, *args, **kwargs):
        return _money_core_schema(cls, args[-1])

    setattr(
        Money,
        "__get_pydantic_core_schema__",
        classmethod(__get_pydantic_core_schema__),
    )

    __all__ = ["_money_core_schema"]
