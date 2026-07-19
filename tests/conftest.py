"""Pytest configuration: make the integration package importable.

The integration lives under ``custom_components/grocery_list``. For pure-Python
unit tests (models, markdown_io, merge, oplog) we don't need Home Assistant
installed; we import the modules directly by putting the package root on the
path.
"""

import sys
import types
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_PKG_PARENT = _ROOT / "custom_components"

for path in (str(_ROOT), str(_PKG_PARENT)):
    if path not in sys.path:
        sys.path.insert(0, path)


def _install_homeassistant_stubs() -> None:
    """Provide minimal Home Assistant stubs for pure-logic unit tests.

    The integration's package ``__init__`` imports a few Home Assistant symbols
    at module load time. Home Assistant is a very heavy dependency and is not
    required to test the pure modules (models, markdown_io, merge, oplog). We
    register just enough of the module tree in ``sys.modules`` so importing
    ``grocery_list`` succeeds without the real framework. Tests that actually
    exercise HA behavior (config flow, coordinator) will run under a real HA
    test harness instead.

    If the real Home Assistant package is installed, we do NOT stub — the real
    framework takes precedence so integration-level tests exercise real code.
    """
    if "homeassistant" in sys.modules:
        return

    import importlib.util

    if importlib.util.find_spec("homeassistant") is not None:
        # Real Home Assistant is installed; let it be imported normally.
        return

    ha = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    core = types.ModuleType("homeassistant.core")

    class _Stub:  # noqa: D401 - simple placeholder
        """Generic placeholder standing in for a Home Assistant class."""

    setattr(config_entries, "ConfigEntry", _Stub)
    setattr(core, "HomeAssistant", _Stub)

    setattr(ha, "config_entries", config_entries)
    setattr(ha, "core", core)

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.config_entries"] = config_entries
    sys.modules["homeassistant.core"] = core


_install_homeassistant_stubs()
