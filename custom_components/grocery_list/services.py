"""Home Assistant services for the Grocery List integration (PLAN §9).

While the custom Lovelace card drives the app through the WebSocket API
(``websocket_api.py``), these services expose the same high-level actions to
Home Assistant *automations, scripts, and voice assistants*. For example, a
voice assistant intent ("add milk to the shopping list") or an automation
("every Monday, clear the checked items") can call these services.

Each service resolves the target :class:`GroceryCoordinator` from an
``entry_id`` (defaulting to the single loaded entry when there is exactly one),
then delegates to the coordinator — identical to the websocket handlers. The
coordinator records the op, updates the model, notifies subscribers, and arms
the debounced push, so a service call and a card action are fully equivalent.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import GroceryCoordinator

_LOGGER = logging.getLogger(__name__)

# Service names.
SERVICE_ADD_ITEM = "add_item"
SERVICE_UPDATE_ITEM = "update_item"
SERVICE_SET_CHECKED = "set_checked"
SERVICE_DELETE_ITEM = "delete_item"
SERVICE_RESTORE_ARCHIVED = "restore_archived"
SERVICE_CLEAR_CHECKED = "clear_checked"
SERVICE_CREATE_LIST = "create_list"
SERVICE_RENAME_LIST = "rename_list"
SERVICE_DELETE_LIST = "delete_list"
SERVICE_REORDER_CATEGORIES = "reorder_categories"
SERVICE_RENAME_CATEGORY = "rename_category"
SERVICE_UNDO = "undo"
SERVICE_REDO = "redo"
SERVICE_SYNC = "sync"

# Common attribute keys.
ATTR_ENTRY_ID = "entry_id"
ATTR_SLUG = "slug"
ATTR_NAME = "name"
ATTR_CATEGORY = "category"
ATTR_QTY_VALUE = "qty_value"
ATTR_QTY_UNIT = "qty_unit"
ATTR_CHECKED = "checked"
ATTR_NEW_NAME = "new_name"
ATTR_NEW_CATEGORY = "new_category"
ATTR_TITLE = "title"
ATTR_ORDER = "order"
ATTR_OLD = "old"
ATTR_NEW = "new"

_ENTRY_ID_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTRY_ID): cv.string})

_ADD_ITEM_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
        vol.Required(ATTR_NAME): cv.string,
        vol.Optional(ATTR_CATEGORY): vol.Any(cv.string, None),
        vol.Optional(ATTR_QTY_VALUE): vol.Coerce(float),
        vol.Optional(ATTR_QTY_UNIT): cv.string,
    }
)

_CLEAR_CHECKED_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
    }
)

_SLUG_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
    }
)

_UPDATE_ITEM_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
        vol.Required(ATTR_NAME): cv.string,
        vol.Optional(ATTR_CATEGORY): vol.Any(cv.string, None),
        vol.Optional(ATTR_NEW_NAME): cv.string,
        vol.Optional(ATTR_NEW_CATEGORY): vol.Any(cv.string, None),
        vol.Optional(ATTR_QTY_VALUE): vol.Any(vol.Coerce(float), None),
        vol.Optional(ATTR_QTY_UNIT): cv.string,
    }
)

_SET_CHECKED_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
        vol.Required(ATTR_NAME): cv.string,
        vol.Optional(ATTR_CATEGORY): vol.Any(cv.string, None),
        vol.Required(ATTR_CHECKED): cv.boolean,
    }
)

_ITEM_KEY_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
        vol.Required(ATTR_NAME): cv.string,
        vol.Optional(ATTR_CATEGORY): vol.Any(cv.string, None),
    }
)

_CREATE_LIST_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_SLUG): cv.string,
    }
)

_RENAME_LIST_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
        vol.Required(ATTR_TITLE): cv.string,
    }
)

_REORDER_CATEGORIES_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
        vol.Required(ATTR_ORDER): vol.All(cv.ensure_list, [cv.string]),
    }
)

_RENAME_CATEGORY_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_SLUG): cv.string,
        vol.Required(ATTR_OLD): cv.string,
        vol.Required(ATTR_NEW): cv.string,
    }
)


@callback
def _resolve_coordinator(
    hass: HomeAssistant, call: ServiceCall
) -> GroceryCoordinator:
    """Return the target coordinator, defaulting to the sole loaded entry.

    If ``entry_id`` is given it must exist. Otherwise, when exactly one entry is
    loaded, that one is used; ambiguity (0 or >1) raises a clear error.
    """
    entries: dict[str, GroceryCoordinator] = hass.data.get(DOMAIN, {})
    entry_id = call.data.get(ATTR_ENTRY_ID)
    if entry_id is not None:
        coordinator = entries.get(entry_id)
        if coordinator is None:
            raise HomeAssistantError(f"No grocery_list entry {entry_id}")
        return coordinator
    if len(entries) == 1:
        return next(iter(entries.values()))
    if not entries:
        raise HomeAssistantError("No grocery_list entries are loaded")
    raise HomeAssistantError(
        "Multiple grocery_list entries are loaded; specify entry_id"
    )


@callback
def async_register(hass: HomeAssistant) -> None:
    """Register all domain services (called once from setup)."""

    async def _add_item(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_add_item(
            call.data[ATTR_SLUG],
            call.data[ATTR_NAME],
            category=call.data.get(ATTR_CATEGORY),
            qty_value=call.data.get(ATTR_QTY_VALUE),
            qty_unit=call.data.get(ATTR_QTY_UNIT),
        )

    async def _update_item(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        changes: dict[str, Any] = {}
        if ATTR_NEW_NAME in call.data:
            changes["new_name"] = call.data[ATTR_NEW_NAME]
        if ATTR_NEW_CATEGORY in call.data:
            changes["new_category"] = call.data[ATTR_NEW_CATEGORY]
        if ATTR_QTY_VALUE in call.data:
            changes["qty_value"] = call.data[ATTR_QTY_VALUE]
        if ATTR_QTY_UNIT in call.data:
            changes["qty_unit"] = call.data[ATTR_QTY_UNIT]
        coordinator.async_update_item(
            call.data[ATTR_SLUG],
            call.data.get(ATTR_CATEGORY),
            call.data[ATTR_NAME],
            **changes,
        )

    async def _set_checked(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_set_checked(
            call.data[ATTR_SLUG],
            call.data.get(ATTR_CATEGORY),
            call.data[ATTR_NAME],
            call.data[ATTR_CHECKED],
        )

    async def _delete_item(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_delete_item(
            call.data[ATTR_SLUG],
            call.data.get(ATTR_CATEGORY),
            call.data[ATTR_NAME],
        )

    async def _restore_archived(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_restore_archived(
            call.data[ATTR_SLUG],
            call.data.get(ATTR_CATEGORY),
            call.data[ATTR_NAME],
        )

    async def _clear_checked(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_clear_checked(call.data[ATTR_SLUG])

    async def _create_list(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_create_list(
            call.data[ATTR_TITLE], slug=call.data.get(ATTR_SLUG)
        )

    async def _rename_list(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_rename_list(
            call.data[ATTR_SLUG], call.data[ATTR_TITLE]
        )

    async def _delete_list(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_delete_list(call.data[ATTR_SLUG])

    async def _reorder_categories(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_reorder_categories(
            call.data[ATTR_SLUG], call.data[ATTR_ORDER]
        )

    async def _rename_category(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_rename_category(
            call.data[ATTR_SLUG], call.data[ATTR_OLD], call.data[ATTR_NEW]
        )

    async def _undo(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_undo()

    async def _redo(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        coordinator.async_redo()

    async def _sync(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        await coordinator.async_sync()

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_ITEM, _add_item, schema=_ADD_ITEM_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_ITEM, _update_item, schema=_UPDATE_ITEM_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_CHECKED, _set_checked, schema=_SET_CHECKED_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_ITEM, _delete_item, schema=_ITEM_KEY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESTORE_ARCHIVED,
        _restore_archived,
        schema=_ITEM_KEY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_CHECKED, _clear_checked, schema=_CLEAR_CHECKED_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CREATE_LIST, _create_list, schema=_CREATE_LIST_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RENAME_LIST, _rename_list, schema=_RENAME_LIST_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_LIST, _delete_list, schema=_SLUG_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REORDER_CATEGORIES,
        _reorder_categories,
        schema=_REORDER_CATEGORIES_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RENAME_CATEGORY,
        _rename_category,
        schema=_RENAME_CATEGORY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UNDO, _undo, schema=_ENTRY_ID_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_REDO, _redo, schema=_ENTRY_ID_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SYNC, _sync, schema=_ENTRY_ID_SCHEMA
    )


@callback
def async_unregister(hass: HomeAssistant) -> None:
    """Remove all domain services (called when the last entry unloads)."""
    for service in (
        SERVICE_ADD_ITEM,
        SERVICE_UPDATE_ITEM,
        SERVICE_SET_CHECKED,
        SERVICE_DELETE_ITEM,
        SERVICE_RESTORE_ARCHIVED,
        SERVICE_CLEAR_CHECKED,
        SERVICE_CREATE_LIST,
        SERVICE_RENAME_LIST,
        SERVICE_DELETE_LIST,
        SERVICE_REORDER_CATEGORIES,
        SERVICE_RENAME_CATEGORY,
        SERVICE_UNDO,
        SERVICE_REDO,
        SERVICE_SYNC,
    ):
        hass.services.async_remove(DOMAIN, service)
