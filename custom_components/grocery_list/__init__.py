"""The Grocery List integration.

Git-synced, Markdown-backed multiple grocery lists for Home Assistant.

This module wires up config-entry setup/teardown. The heavy lifting (git
transport, semantic merge, sync coordinator, websocket API) lives in dedicated
modules and is attached to the config entry runtime data as it is implemented.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from . import services, websocket_api
from .const import DOMAIN
from .coordinator import GroceryCoordinator
from .frontend import async_register_card
from .git_backend import GitAuthError, GitBackendError

_LOGGER = logging.getLogger(__name__)

# No entity platforms yet; the UI is a custom Lovelace card talking over the
# websocket API. Platforms may be added later (e.g. a `todo` bridge).
PLATFORMS: list[str] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Grocery List from a config entry."""
    entries = hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug("Setting up Grocery List entry %s", entry.entry_id)

    # Register the websocket commands and domain services once (they are
    # global, not per-entry). Handlers resolve the target coordinator by
    # entry_id at call time, so registering on the first entry is sufficient.
    if not entries:
        websocket_api.async_register(hass)
        services.async_register(hass)
        await async_register_card(hass)

    coordinator = GroceryCoordinator(hass, entry)
    try:
        await coordinator.async_setup()
    except GitAuthError as err:
        # Bad credentials won't fix themselves on retry — surface clearly.
        raise ConfigEntryNotReady(f"Git authentication failed: {err}") from err
    except GitBackendError as err:
        # Transient/offline — HA will retry setup later.
        raise ConfigEntryNotReady(f"Git backend unavailable: {err}") from err

    hass.data[DOMAIN][entry.entry_id] = coordinator

    if PLATFORMS:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = True
    if PLATFORMS:
        unload_ok = await hass.config_entries.async_unload_platforms(
            entry, PLATFORMS
        )

    if unload_ok:
        coordinator: GroceryCoordinator | None = hass.data[DOMAIN].pop(
            entry.entry_id, None
        )
        if coordinator is not None:
            await coordinator.async_shutdown()

        # Remove global services once the last entry is gone. Websocket
        # commands cannot be unregistered, but they are harmless without any
        # loaded entry (handlers return a not-found error).
        if not hass.data[DOMAIN]:
            services.async_unregister(hass)

    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Handle options updates by reloading the entry."""
    await hass.config_entries.async_reload(entry.entry_id)
