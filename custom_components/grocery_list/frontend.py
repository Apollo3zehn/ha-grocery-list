"""Serve and auto-register the custom Lovelace card as a Lovelace resource.

The built card (``frontend/grocery-list-card.js``) is shipped *inside* the
integration so HACS delivers a single artifact. Rather than making users add a
Lovelace resource by hand, we:

1. Register a cached static path that serves the ``frontend/`` directory, and
2. Register the card in Home Assistant's Lovelace **resource storage
   collection** as a ``module`` resource.

Why a Lovelace resource and not ``add_extra_js_url``?
----------------------------------------------------
``add_extra_js_url`` injects a ``<script type="module">`` into ``index.html``
that loads *in parallel* with the frontend app. On a normal reload the browser
can render a ``<grocery-list-card>`` tag before ``customElements.define`` has
run, yielding the dreaded "Custom element doesn't exist: grocery-list-card"
(which then "fixes itself" after a hard reload because the timing shifts). The
frontend loads registered **Lovelace resources** deterministically before it
renders cards, so registering as a resource eliminates that race entirely.

This path only works in Lovelace **storage mode** (the default). In YAML mode
the resource collection is read-only and users manage resources themselves, so
we log a clear instruction and do nothing else.

Registration is process-global (not per config entry) and guarded so it only
happens once even with multiple entries.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    FRONTEND_CARD_FILENAME,
    FRONTEND_CARD_URL,
    FRONTEND_DIR,
    FRONTEND_URL_BASE,
)

_LOGGER = logging.getLogger(__name__)

# Marker in hass.data so we register the static path + resource exactly once for
# the whole process, regardless of how many config entries are loaded.
_REGISTERED_KEY = f"{DOMAIN}_frontend_registered"


def _read_card_bytes(card_file: Path) -> bytes | None:
    """Blocking read of the built card bytes; ``None`` if missing.

    Runs in the executor (see :func:`async_register_card`) because both the
    ``stat`` implied by :meth:`Path.is_file` and :meth:`Path.read_bytes` are
    blocking filesystem I/O that must not happen on the event loop.
    """
    if not card_file.is_file():
        return None
    try:
        return card_file.read_bytes()
    except OSError:
        return None


def _card_cache_tag(card_bytes: bytes) -> str:
    """Content-based cache-busting tag derived from the built JS bytes.

    We hash the built JS bytes rather than using the integration version so the
    URL changes on *every* rebuild of the card, even within the same release.
    This matters because HA's frontend service worker (PWA cache) will otherwise
    keep serving a previously cached module for an unchanged URL. A short hex
    digest is plenty to distinguish builds and keeps the URL tidy.
    """
    return hashlib.sha256(card_bytes).hexdigest()[:12]


async def async_register_card(hass: HomeAssistant) -> None:
    """Serve the card dir and register the card as a Lovelace resource.

    Idempotent for the process and idempotent against the resource store: on
    repeat runs (e.g. after a rebuild) we update the existing resource's URL to
    refresh the cache-busting tag instead of creating duplicates.
    """
    if hass.data.get(_REGISTERED_KEY):
        return

    frontend_dir = Path(__file__).parent / FRONTEND_DIR
    card_file = frontend_dir / FRONTEND_CARD_FILENAME

    # Read the built card off the event loop: is_file()/read_bytes() are
    # blocking filesystem I/O and HA flags them if run on the loop.
    card_bytes = await hass.async_add_executor_job(_read_card_bytes, card_file)
    if card_bytes is None:
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

    url = f"{FRONTEND_CARD_URL}?v={_card_cache_tag(card_bytes)}"
    await _async_register_resource(hass, url)

    hass.data[_REGISTERED_KEY] = True


async def _async_register_resource(hass: HomeAssistant, url: str) -> None:
    """Create or update our card entry in the Lovelace resource collection.

    Only works in Lovelace *storage* mode. In YAML mode the collection is a
    read-only :class:`ResourceYAMLCollection`; we detect that and log how to add
    the resource manually.
    """
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        _LOGGER.warning(
            "Lovelace is not set up yet; cannot register the Grocery List card "
            "resource. The card will be unavailable until Lovelace loads."
        )
        return

    resources = lovelace_data.resources
    if not isinstance(resources, ResourceStorageCollection):
        # YAML resource mode -> read-only. Tell the user how to add it.
        _LOGGER.warning(
            "Lovelace is in YAML resource mode; add the Grocery List card "
            "manually under lovelace.resources:\n  - url: %s\n    type: module",
            url,
        )
        return

    # Ensure the collection is loaded before we inspect/modify it.
    if not resources.loaded:
        await resources.async_load()
        resources.loaded = True

    # De-dupe by URL base (ignoring the ?v= cache tag): update in place if we
    # already registered a (possibly older) build, else create a fresh entry.
    url_base = url.split("?", 1)[0]
    for item in resources.async_items():
        existing = item.get("url", "")
        if existing.split("?", 1)[0] == url_base:
            if existing != url:
                await resources.async_update_item(
                    item["id"], {"res_type": "module", "url": url}
                )
                _LOGGER.debug("Updated Grocery List card resource -> %s", url)
            else:
                _LOGGER.debug("Grocery List card resource already current")
            return

    await resources.async_create_item({"res_type": "module", "url": url})
    _LOGGER.debug("Registered Grocery List card resource at %s", url)
