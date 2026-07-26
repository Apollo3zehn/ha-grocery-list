"""Tests for the developer-maintained units loader (PLAN §4.3)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_UNITS_PATH = Path(__file__).resolve().parents[1] / "custom_components/grocery_list/units.py"
_SPEC = importlib.util.spec_from_file_location("grocery_list_units", _UNITS_PATH)
assert _SPEC and _SPEC.loader
units = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(units)


def test_load_units_returns_shipped_set():
    loaded = units.load_units()
    ids = {u["id"] for u in loaded}
    # A representative sample from units.yaml.
    assert {"pcs", "g", "kg", "ml", "l", "jar"} <= ids


def test_each_unit_has_id_and_labels():
    for u in units.load_units():
        assert u["id"]
        assert isinstance(u["labels"], dict)
        assert "en" in u["labels"]
        for label in u["labels"].values():
            assert isinstance(label, str) or (
                isinstance(label, dict)
                and isinstance(label.get("one"), str)
                and isinstance(label.get("other"), str)
            )


def test_default_unit_is_pcs():
    assert units.default_unit_id() == "pcs"


def test_units_are_cached():
    # lru_cache: repeated calls return the same object.
    assert units.load_units() is units.load_units()
