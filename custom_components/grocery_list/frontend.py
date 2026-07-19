"""Serve and auto-load the custom Lovelace card (PLAN §13 polish).

The built card (``frontend/grocery-list-card.js``) is shipped *inside* the
integration so HACS delivers a single artifact. Rather than making users add a
Lovelace resource by hand, we:

1. Register a cached static path that serves the ``frontend/`` directory, and
2. Register the card as an extra frontend module via
   :func:`homeassistant.components.frontend.add_extra_js_url`.

``add_extra_js_url`` is preferred over poking the Lovelace resource storage
collection because it works in *both* storage and YAML dashboard modes and does
not mutate the user's stored config. The module is loaded on every dashboard,
which is exactly what a globally-available custom card wants.

Registration is process-global (not per config entry) and guarded so it only
happens once even with multiple entries.
"""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    FRONTEND_CARD_FILENAME,
    FRONTEND_CARD_URL,
    FRONTEND_DIR,
    FRONTEND_URL_BASE,
)

_LOGGER = logging.getLogger(__name__)

# Marker in hass.data so we register the static path + module exactly once for
# the whole process, regardless of how many config entries are loaded.
_REGISTERED_KEY = f"{DOMAIN}_frontend_registered"


def _card_version(hass: HomeAssistant) -> str:
    """Best-effort integration version for cache-busting the card URL."""
    try:
        integration = hass.data["integrations"][DOMAIN]  # type: ignore[index]
        version = getattr(integration, "version", None)
        if version:
            return str(version)
    except (KeyError, AttributeError):
        pass
    return "0"


async def async_register_card(hass: HomeAssistant) -> None:
    """Serve the card dir and auto-load the card module (idempotent)."""
    if hass.data.get(_REGISTERED_KEY):
        return

    frontend_dir = Path(__file__).parent / FRONTEND_DIR
    card_file = frontend_dir / FRONTEND_CARD_FILENAME
    if not card_file.is_file():
        # The integration is still usable via services/websocket even without
        # the card; warn loudly so a broken build is obvious.
        _LOGGER.warning(
            "Grocery List card asset missing at %s; the custom card will not "
            "be available. Did the frontend build run?",
            card_file,
        )
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL_BASE, str(frontend_dir), True)]
    )

    # Cache-bust on upgrade so browsers pick up a new build.
    url = f"{FRONTEND_CARD_URL}?v={_card_version(hass)}"
    add_extra_js_url(hass, url)

    hass.data[_REGISTERED_KEY] = True
    _LOGGER.debug("Registered Grocery List card module at %s", url)
