"""Tests for the Grocery List WebSocket API (PLAN §9).

We avoid the git-backed ``async_setup`` path: instead we construct a
:class:`GroceryCoordinator` directly (as in ``test_coordinator``), inject it
into ``hass.data[DOMAIN][entry_id]``, register the websocket commands, and drive
them through a real websocket client. This exercises the command schemas,
routing, coordinator delegation, and the subscribe/snapshot push path.
"""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant

from custom_components.grocery_list import websocket_api
from custom_components.grocery_list.const import (
    CONF_AUTH_METHOD,
    CONF_BRANCH,
    CONF_IDENTITY,
    CONF_REPO_URL,
    DOMAIN,
)
from custom_components.grocery_list.coordinator import GroceryCoordinator


@pytest.fixture
async def setup_ws(hass: HomeAssistant):
    """Register WS commands + a coordinator, return (entry_id, coordinator)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="kitchen-pi",
        data={
            CONF_IDENTITY: "kitchen-pi",
            CONF_AUTH_METHOD: "https",
            CONF_REPO_URL: "https://example.com/x/y.git",
            CONF_BRANCH: "main",
        },
    )
    entry.add_to_hass(hass)
    coordinator = GroceryCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    websocket_api.async_register(hass)
    return entry.entry_id, coordinator


async def test_subscribe_sends_initial_snapshot(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    coordinator.async_add_item("rewe", "Tomatoes", qty_value=2, qty_unit="pcs")
    client = await hass_ws_client(hass)

    await client.send_json(
        {"id": 1, "type": "grocery_list/subscribe", "entry_id": entry_id}
    )
    result = await client.receive_json()
    assert result["success"] is True

    # The initial snapshot arrives as an event message.
    event = await client.receive_json()
    snap = event["event"]
    assert snap["identity"] == "kitchen-pi"
    assert snap["lists"][0]["slug"] == "rewe"
    assert snap["lists"][0]["items"][0]["name"] == "Tomatoes"


async def test_subscribe_pushes_on_change(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    client = await hass_ws_client(hass)
    await client.send_json(
        {"id": 1, "type": "grocery_list/subscribe", "entry_id": entry_id}
    )
    await client.receive_json()  # success
    await client.receive_json()  # initial (empty) snapshot

    # A mutation via the coordinator should push a new snapshot event.
    coordinator.async_add_item("rewe", "Milk")
    event = await client.receive_json()
    names = [i["name"] for i in event["event"]["lists"][0]["items"]]
    assert "Milk" in names


async def test_subscribe_unknown_entry_errors(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    client = await hass_ws_client(hass)
    await client.send_json(
        {"id": 1, "type": "grocery_list/subscribe", "entry_id": "nope"}
    )
    result = await client.receive_json()
    assert result["success"] is False
    assert result["error"]["code"] == "not_found"


async def test_add_item_command(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/add_item",
            "entry_id": entry_id,
            "slug": "rewe",
            "name": "Bread",
            "qty_value": 1,
            "qty_unit": "pcs",
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["item"]["name"] == "Bread"
    assert "rewe" in coordinator.state.lists


async def test_update_item_command(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    item = coordinator.async_add_item("rewe", "Bread")
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/update_item",
            "entry_id": entry_id,
            "slug": "rewe",
            "item_id": item.id,
            "name": "Whole Grain Bread",
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["item"]["name"] == "Whole Grain Bread"


async def test_update_missing_item_errors(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, _ = setup_ws
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/update_item",
            "entry_id": entry_id,
            "slug": "rewe",
            "item_id": "missing",
            "name": "X",
        }
    )
    result = await client.receive_json()
    assert result["success"] is False
    assert result["error"]["code"] == "not_found"


async def test_set_checked_command(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    item = coordinator.async_add_item("rewe", "Bread")
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/set_checked",
            "entry_id": entry_id,
            "slug": "rewe",
            "item_id": item.id,
            "checked": True,
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["item"]["checked"] is True


async def test_delete_item_command(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    item = coordinator.async_add_item("rewe", "Bread")
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/delete_item",
            "entry_id": entry_id,
            "slug": "rewe",
            "item_id": item.id,
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["deleted"] == item.id


async def test_clear_checked_command(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    a = coordinator.async_add_item("rewe", "A")
    coordinator.async_add_item("rewe", "B")
    coordinator.async_set_checked("rewe", a.id, True)
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/clear_checked",
            "entry_id": entry_id,
            "slug": "rewe",
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["cleared"] == [a.id]


async def test_category_lifecycle_commands(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    client = await hass_ws_client(hass)

    # Create
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/create_category",
            "entry_id": entry_id,
            "labels": {"en": "Vegetables", "de": "Gem\u00fcse"},
            "icon": "mdi:carrot",
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    cat_id = result["result"]["category"]["id"]

    # Update
    await client.send_json(
        {
            "id": 2,
            "type": "grocery_list/update_category",
            "entry_id": entry_id,
            "cat_id": cat_id,
            "icon": "mdi:food-apple",
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["category"]["icon"] == "mdi:food-apple"

    # Delete
    await client.send_json(
        {
            "id": 3,
            "type": "grocery_list/delete_category",
            "entry_id": entry_id,
            "cat_id": cat_id,
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["deleted"] == cat_id


async def test_reorder_categories_command(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    c1 = coordinator.async_create_category({"en": "A"})
    c2 = coordinator.async_create_category({"en": "B"})
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/reorder_categories",
            "entry_id": entry_id,
            "ordered_ids": [c2.id, c1.id],
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert coordinator.state.categories.order_ids() == [c2.id, c1.id]


async def test_get_units_command(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    """get_units is global (no entry_id) and returns the shipped unit list."""
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": "grocery_list/get_units"})
    result = await client.receive_json()
    assert result["success"] is True
    ids = {u["id"] for u in result["result"]["units"]}
    assert "pcs" in ids
    assert result["result"]["default_unit"] == "pcs"


async def test_undo_redo_commands(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    item = coordinator.async_add_item("rewe", "Bread")
    client = await hass_ws_client(hass)

    await client.send_json(
        {"id": 1, "type": "grocery_list/undo", "entry_id": entry_id}
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["undone"] is True
    assert item.id not in coordinator.state.lists["rewe"].items

    await client.send_json(
        {"id": 2, "type": "grocery_list/redo", "entry_id": entry_id}
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["redone"] is True


async def test_list_lifecycle_commands(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, coordinator = setup_ws
    client = await hass_ws_client(hass)

    # Create
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/create_list",
            "entry_id": entry_id,
            "title": "Weekend BBQ",
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    slug = result["result"]["list"]["slug"]
    assert slug == "weekend-bbq"

    # Rename
    await client.send_json(
        {
            "id": 2,
            "type": "grocery_list/rename_list",
            "entry_id": entry_id,
            "slug": slug,
            "title": "Sunday BBQ",
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["list"]["title"] == "Sunday BBQ"

    # Delete
    await client.send_json(
        {
            "id": 3,
            "type": "grocery_list/delete_list",
            "entry_id": entry_id,
            "slug": slug,
        }
    )
    result = await client.receive_json()
    assert result["success"] is True
    assert result["result"]["deleted"] == slug
    assert slug not in coordinator.state.lists


async def test_rename_missing_list_errors(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, _ = setup_ws
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/rename_list",
            "entry_id": entry_id,
            "slug": "missing",
            "title": "X",
        }
    )
    result = await client.receive_json()
    assert result["success"] is False
    assert result["error"]["code"] == "not_found"


async def test_delete_missing_list_errors(
    hass: HomeAssistant, hass_ws_client, setup_ws
):
    entry_id, _ = setup_ws
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": "grocery_list/delete_list",
            "entry_id": entry_id,
            "slug": "missing",
        }
    )
    result = await client.receive_json()
    assert result["success"] is False
    assert result["error"]["code"] == "not_found"
