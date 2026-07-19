"""Developer-maintained unit definitions loader (PLAN §4.3).

Units are structured (id + per-locale labels), NOT free text, and are shipped
with the integration in ``units.yaml`` rather than being user-managed (unlike
categories). The card needs the unit list to render its quantity value+unit
stepper, so this module loads and caches the YAML and exposes a JSON-safe list
for the websocket API.

The file is loaded once and cached at module level; it is small and static for
the lifetime of the process. Loading is synchronous file I/O, so callers on the
event loop should invoke :func:`async_load_units` (which offloads to an
executor) rather than :func:`load_units` directly.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import yaml

_UNITS_FILE = os.path.join(os.path.dirname(__file__), "units.yaml")


@lru_cache(maxsize=1)
def load_units() -> list[dict[str, Any]]:
    """Load and cache the unit definitions as a list of plain dicts.

    Each entry is ``{"id": str, "default": bool, "labels": {locale: str}}``.
    Malformed or missing files yield an empty list rather than raising, so the
    card degrades gracefully (it can still add items without a unit).
    """
    try:
        with open(_UNITS_FILE, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except (OSError, yaml.YAMLError):
        return []

    raw_units = data.get("units", []) if isinstance(data, dict) else []
    units: list[dict[str, Any]] = []
    for entry in raw_units:
        if not isinstance(entry, dict) or "id" not in entry:
            continue
        units.append(
            {
                "id": str(entry["id"]),
                "default": bool(entry.get("default", False)),
                "labels": dict(entry.get("labels") or {}),
            }
        )
    return units


def default_unit_id() -> str:
    """Return the id of the unit flagged ``default`` (fallback ``pcs``)."""
    for unit in load_units():
        if unit["default"]:
            return unit["id"]
    return "pcs"


async def async_load_units(hass) -> list[dict[str, Any]]:
    """Load units off the event loop (cached after first call)."""
    return await hass.async_add_executor_job(load_units)
