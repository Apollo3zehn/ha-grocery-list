"""WebSocket API for the Grocery List custom Lovelace card (PLAN §9).

The card is a custom TS+Lit element that talks to HA over the WebSocket API.
This module registers a family of ``grocery_list/*`` commands that:

- **subscribe** to a config entry's state (initial snapshot + push on change),
- **mutate** state (add/update/check/delete item, clear-checked, category CRUD,
  reorder), and
- drive **undo/redo** and an explicit **sync** trigger.

Every mutation is delegated to :class:`GroceryCoordinator`, which records the
op, updates the in-memory model, notifies listeners, and arms the debounced push
(PLAN §5/§6). The command handlers here are thin: validate args, locate the
coordinator for ``entry_id``, call the coordinator method, and reply.

WHY a subscription model: multiple dashboards/devices can be open at once; each
subscribes and receives the full JSON snapshot whenever anything changes
(local edit, undo/redo, or a pull that merged remote changes). The snapshot is
intentionally simple/whole rather than diff-based — grocery lists are small and
correctness/robustness matter more than payload size.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from . import units as units_mod
from .const import DOMAIN
from .coordinator import GroceryCoordinator

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Command type strings (namespaced under the domain).
# ---------------------------------------------------------------------------
WS_SUBSCRIBE = f"{DOMAIN}/subscribe"
WS_ADD_ITEM = f"{DOMAIN}/add_item"
WS_UPDATE_ITEM = f"{DOMAIN}/update_item"
WS_SET_CHECKED = f"{DOMAIN}/set_checked"
WS_DELETE_ITEM = f"{DOMAIN}/delete_item"
WS_CLEAR_CHECKED = f"{DOMAIN}/clear_checked"
WS_CREATE_CATEGORY = f"{DOMAIN}/create_category"
WS_UPDATE_CATEGORY = f"{DOMAIN}/update_category"
WS_DELETE_CATEGORY = f"{DOMAIN}/delete_category"
WS_REORDER_CATEGORIES = f"{DOMAIN}/reorder_categories"
WS_UNDO = f"{DOMAIN}/undo"
WS_REDO = f"{DOMAIN}/redo"
WS_SYNC = f"{DOMAIN}/sync"
WS_GET_UNITS = f"{DOMAIN}/get_units"


@callback
def _get_coordinator(
    hass: HomeAssistant, entry_id: str
) -> GroceryCoordinator | None:
    """Locate the coordinator for a config entry id (or None if not loaded)."""
    return hass.data.get(DOMAIN, {}).get(entry_id)


@callback
def _require_coordinator(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> GroceryCoordinator | None:
    """Resolve the coordinator or send a standard not-found error."""
    coordinator = _get_coordinator(hass, msg["entry_id"])
    if coordinator is None:
        connection.send_error(
            msg["id"],
            websocket_api.const.ERR_NOT_FOUND,
            f"No grocery_list entry {msg['entry_id']}",
        )
        return None
    return coordinator


@callback
def async_register(hass: HomeAssistant) -> None:
    """Register all websocket command handlers (called once from setup)."""
    websocket_api.async_register_command(hass, ws_subscribe)
    websocket_api.async_register_command(hass, ws_add_item)
    websocket_api.async_register_command(hass, ws_update_item)
    websocket_api.async_register_command(hass, ws_set_checked)
    websocket_api.async_register_command(hass, ws_delete_item)
    websocket_api.async_register_command(hass, ws_clear_checked)
    websocket_api.async_register_command(hass, ws_create_category)
    websocket_api.async_register_command(hass, ws_update_category)
    websocket_api.async_register_command(hass, ws_delete_category)
    websocket_api.async_register_command(hass, ws_reorder_categories)
    websocket_api.async_register_command(hass, ws_undo)
    websocket_api.async_register_command(hass, ws_redo)
    websocket_api.async_register_command(hass, ws_sync)
    websocket_api.async_register_command(hass, ws_get_units)


# ---------------------------------------------------------------------------
# Subscription
# ---------------------------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SUBSCRIBE,
        vol.Required("entry_id"): str,
        vol.Optional("locale", default="en"): str,
    }
)
@callback
def ws_subscribe(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Subscribe to a list's state: send a snapshot now and on every change."""
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    locale = msg["locale"]

    @callback
    def _forward() -> None:
        connection.send_message(
            websocket_api.event_message(
                msg["id"], coordinator.snapshot(locale=locale)
            )
        )

    remove = coordinator.async_add_listener(_forward)
    connection.subscriptions[msg["id"]] = remove
    connection.send_result(msg["id"])
    # Push the initial snapshot immediately after confirming the subscription.
    _forward()


# ---------------------------------------------------------------------------
# Item mutations
# ---------------------------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_ADD_ITEM,
        vol.Required("entry_id"): str,
        vol.Required("slug"): str,
        vol.Required("name"): str,
        vol.Optional("category"): vol.Any(str, None),
        vol.Optional("qty_value"): vol.Any(float, int, None),
        vol.Optional("qty_unit"): vol.Any(str, None),
    }
)
@callback
def ws_add_item(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    item = coordinator.async_add_item(
        msg["slug"],
        msg["name"],
        category=msg.get("category"),
        qty_value=msg.get("qty_value"),
        qty_unit=msg.get("qty_unit"),
    )
    connection.send_result(msg["id"], {"item": item.to_dict()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_UPDATE_ITEM,
        vol.Required("entry_id"): str,
        vol.Required("slug"): str,
        vol.Required("item_id"): str,
        vol.Optional("name"): str,
        vol.Optional("category"): vol.Any(str, None),
        vol.Optional("qty_value"): vol.Any(float, int, None),
        vol.Optional("qty_unit"): vol.Any(str, None),
    }
)
@callback
def ws_update_item(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    # Only forward keys the caller actually sent so we don't clobber fields.
    changes: dict[str, Any] = {}
    for key in ("name", "category", "qty_value", "qty_unit"):
        if key in msg:
            changes[key] = msg[key]
    item = coordinator.async_update_item(msg["slug"], msg["item_id"], **changes)
    if item is None:
        connection.send_error(
            msg["id"], websocket_api.const.ERR_NOT_FOUND, "Item not found"
        )
        return
    connection.send_result(msg["id"], {"item": item.to_dict()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SET_CHECKED,
        vol.Required("entry_id"): str,
        vol.Required("slug"): str,
        vol.Required("item_id"): str,
        vol.Required("checked"): bool,
    }
)
@callback
def ws_set_checked(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    item = coordinator.async_set_checked(
        msg["slug"], msg["item_id"], msg["checked"]
    )
    if item is None:
        connection.send_error(
            msg["id"], websocket_api.const.ERR_NOT_FOUND, "Item not found"
        )
        return
    connection.send_result(msg["id"], {"item": item.to_dict()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_DELETE_ITEM,
        vol.Required("entry_id"): str,
        vol.Required("slug"): str,
        vol.Required("item_id"): str,
    }
)
@callback
def ws_delete_item(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    ok = coordinator.async_delete_item(msg["slug"], msg["item_id"])
    if not ok:
        connection.send_error(
            msg["id"], websocket_api.const.ERR_NOT_FOUND, "Item not found"
        )
        return
    connection.send_result(msg["id"], {"deleted": msg["item_id"]})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_CLEAR_CHECKED,
        vol.Required("entry_id"): str,
        vol.Required("slug"): str,
    }
)
@callback
def ws_clear_checked(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    cleared = coordinator.async_clear_checked(msg["slug"])
    connection.send_result(msg["id"], {"cleared": cleared})


# ---------------------------------------------------------------------------
# Category mutations
# ---------------------------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_CREATE_CATEGORY,
        vol.Required("entry_id"): str,
        vol.Required("labels"): {str: str},
        vol.Optional("icon"): vol.Any(str, None),
    }
)
@callback
def ws_create_category(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    cat = coordinator.async_create_category(
        dict(msg["labels"]), icon=msg.get("icon")
    )
    connection.send_result(msg["id"], {"category": cat.to_dict()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_UPDATE_CATEGORY,
        vol.Required("entry_id"): str,
        vol.Required("cat_id"): str,
        vol.Optional("labels"): {str: str},
        vol.Optional("icon"): vol.Any(str, None),
        vol.Optional("order"): int,
    }
)
@callback
def ws_update_category(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    cat = coordinator.async_update_category(
        msg["cat_id"],
        labels=dict(msg["labels"]) if "labels" in msg else None,
        icon=msg.get("icon") if "icon" in msg else None,
        order=msg.get("order") if "order" in msg else None,
    )
    if cat is None:
        connection.send_error(
            msg["id"], websocket_api.const.ERR_NOT_FOUND, "Category not found"
        )
        return
    connection.send_result(msg["id"], {"category": cat.to_dict()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_DELETE_CATEGORY,
        vol.Required("entry_id"): str,
        vol.Required("cat_id"): str,
    }
)
@callback
def ws_delete_category(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    ok = coordinator.async_delete_category(msg["cat_id"])
    if not ok:
        connection.send_error(
            msg["id"], websocket_api.const.ERR_NOT_FOUND, "Category not found"
        )
        return
    connection.send_result(msg["id"], {"deleted": msg["cat_id"]})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_REORDER_CATEGORIES,
        vol.Required("entry_id"): str,
        vol.Required("ordered_ids"): [str],
    }
)
@callback
def ws_reorder_categories(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    coordinator.async_reorder_categories(list(msg["ordered_ids"]))
    connection.send_result(msg["id"], {"ok": True})


# ---------------------------------------------------------------------------
# Undo / redo / sync
# ---------------------------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_UNDO,
        vol.Required("entry_id"): str,
    }
)
@callback
def ws_undo(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    connection.send_result(msg["id"], {"undone": coordinator.async_undo()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_REDO,
        vol.Required("entry_id"): str,
    }
)
@callback
def ws_redo(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    connection.send_result(msg["id"], {"redone": coordinator.async_redo()})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SYNC,
        vol.Required("entry_id"): str,
    }
)
@websocket_api.async_response
async def ws_sync(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Force an immediate sync (pull+merge+push). Async: awaits the flow."""
    coordinator = _require_coordinator(hass, connection, msg)
    if coordinator is None:
        return
    await coordinator.async_sync()
    connection.send_result(msg["id"], {"sync_state": coordinator.sync_state})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_GET_UNITS,
    }
)
@websocket_api.async_response
async def ws_get_units(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the developer-maintained unit list for the qty stepper (PLAN §4.3).

    Units are global (not per-entry), so no ``entry_id`` is required. The first
    call reads and caches ``units.yaml`` off the event loop.
    """
    units = await units_mod.async_load_units(hass)
    connection.send_result(
        msg["id"],
        {"units": units, "default_unit": units_mod.default_unit_id()},
    )
