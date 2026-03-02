"""
In-memory state/conversation memory for Factory.ai bots.

Bots can use :class:`StateStore` to persist conversation context between
turns without depending on an external data store during development.
"""

from __future__ import annotations

from typing import Any


class StateStore:
    """Simple key-value state store for a single bot session.

    Parameters
    ----------
    initial:
        Optional dictionary of initial state values.
    """

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        self._store: dict[str, Any] = dict(initial or {})

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for *key*, or *default* if absent."""
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key*."""
        self._store[key] = value

    def delete(self, key: str) -> None:
        """Remove *key* from the store (no-op if missing)."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the store."""
        self._store.clear()

    def snapshot(self) -> dict[str, Any]:
        """Return a shallow copy of the current state."""
        return dict(self._store)
