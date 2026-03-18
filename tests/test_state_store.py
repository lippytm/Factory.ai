"""Tests for components/memory/state_store.py."""

from __future__ import annotations

from components.memory.state_store import StateStore


class TestStateStore:
    def test_get_missing_key_returns_default(self):
        store = StateStore()
        assert store.get("missing") is None

    def test_get_custom_default(self):
        store = StateStore()
        assert store.get("missing", 42) == 42

    def test_set_and_get(self):
        store = StateStore()
        store.set("key", "value")
        assert store.get("key") == "value"

    def test_initial_state_loaded(self):
        store = StateStore({"a": 1, "b": 2})
        assert store.get("a") == 1
        assert store.get("b") == 2

    def test_overwrite_existing_key(self):
        store = StateStore({"x": "old"})
        store.set("x", "new")
        assert store.get("x") == "new"

    def test_delete_existing_key(self):
        store = StateStore({"k": "v"})
        store.delete("k")
        assert store.get("k") is None

    def test_delete_missing_key_is_noop(self):
        store = StateStore()
        store.delete("nonexistent")  # Should not raise

    def test_clear_removes_all_keys(self):
        store = StateStore({"a": 1, "b": 2})
        store.clear()
        assert store.snapshot() == {}

    def test_snapshot_returns_copy(self):
        store = StateStore({"a": 1})
        snap = store.snapshot()
        snap["a"] = 99  # mutate copy
        assert store.get("a") == 1  # original unchanged

    def test_snapshot_reflects_current_state(self):
        store = StateStore()
        store.set("x", 10)
        store.set("y", 20)
        assert store.snapshot() == {"x": 10, "y": 20}

    def test_none_initial_treated_as_empty(self):
        store = StateStore(None)
        assert store.snapshot() == {}

    def test_set_various_value_types(self):
        store = StateStore()
        store.set("list", [1, 2, 3])
        store.set("dict", {"nested": True})
        store.set("none_val", None)
        assert store.get("list") == [1, 2, 3]
        assert store.get("dict") == {"nested": True}
        assert store.get("none_val") is None
