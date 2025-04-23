"""
Pydantic v2 integration for fxmoney.Money.
Registers a CoreSchema for Money so that any BaseModel field of type Money
is (de)serialized as {"amount": "...", "currency": "..."}.
"""

from __future__ import annotations

try:
    from pydantic import TypeAdapter
    from pydantic_core import core_schema
    from .core import Money
except ImportError:
    # pydantic not installed → skip registration
    __all__ = []
else:
    def _money_core_schema(_type: type[Money], _handler: core_schema.GetCoreSchemaHandler) -> core_schema.CoreSchema:
        """
        CoreSchema that:
        - structures a dict {"amount": str, "currency": str} → Money.from_dict
        - serializes Money → plain dict via Money.to_dict()
        """
        return core_schema.no_info_after_validator_function(
            # Structure: dict → Money
            Money.from_dict,
            # Input schema: object with amount:string and currency:string
            core_schema.json_schema({
                "type": "object",
                "properties": {
                    "amount": {"type": "string"},
                    "currency": {"type": "string"}
                },
                "required": ["amount", "currency"],
                "additionalProperties": False
            }),
            # Serialization: Money → dict
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda m, _: m.to_dict()
            ),
        )

    # Register the adapter globally
    TypeAdapter.register_type_adapter(Money, _money_core_schema)

    __all__ = ["_money_core_schema"]
