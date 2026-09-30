"""
Rule registry — the "no core modification" guarantee.

Drop a new Python file, apply @register_rule, and the engine picks it up
automatically on next start. The engine itself never changes.
"""
from .base import RuleTier

_REGISTRY: dict[str, type] = {}


def register_rule(cls):
    """
    Decorator. Registers a FraudRule subclass in the global registry.
    """
    _REGISTRY[cls.name] = cls
    return cls


def get_rules_by_tier(tier: RuleTier) -> list:
    """Return instantiated rule objects for a given tier."""
    return [cls() for cls in _REGISTRY.values() if cls.tier == tier]


def get_all_rules() -> dict[str, type]:
    """Return the full registry (for introspection/debugging)."""
    return dict(_REGISTRY)
