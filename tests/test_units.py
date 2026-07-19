"""Tests for the developer-maintained units loader (PLAN §4.3)."""

from __future__ import annotations

from custom_components.grocery_list import units


def test_load_units_returns_shipped_set():
    loaded = units.load_units()
    ids = {u["id"] for u in loaded}
    # A representative sample from units.yaml.
    assert {"pcs", "g", "kg", "ml", "l"} <= ids


def test_each_unit_has_id_and_labels():
    for u in units.load_units():
        assert u["id"]
        assert isinstance(u["labels"], dict)
        assert "en" in u["labels"]


def test_default_unit_is_pcs():
    assert units.default_unit_id() == "pcs"


def test_units_are_cached():
    # lru_cache: repeated calls return the same object.
    assert units.load_units() is units.load_units()
