"""Tests for the coordinator's local-only mutation + snapshot behavior.

These use a real ``GroceryCoordinator`` in local-only mode (sync disabled) on a
real in-memory Home Assistant instance provided by
``pytest-homeassistant-custom-component``. No git remote is involved.

Items are addressed by identity ``(category, name)``.
"""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.grocery_list.const import (
    CONF_AUTH_METHOD,
    CONF_BRANCH,
    CONF_IDENTITY,
    CONF_REPO_URL,
    CONF_SYNC_ENABLED,
    DOMAIN,
)
from custom_components.grocery_list.coordinator import GroceryCoordinator

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


@pytest.fixture
def entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_IDENTITY: "kitchen-pi",
            CONF_REPO_URL: "",
            CONF_AUTH_METHOD: "ssh",
            CONF_BRANCH: "main",
            CONF_SYNC_ENABLED: False,
        },
    )


@pytest.fixture
async def coord(hass: HomeAssistant, entry: MockConfigEntry) -> GroceryCoordinator:
    entry.add_to_hass(hass)
    c = GroceryCoordinator(hass, entry)
    await c.async_setup()
    return c


async def test_add_item_creates_list_and_item(coord: GroceryCoordinator):
    item = coord.async_add_item("rewe", "Milk", category="Dairy")
    assert item.key == "Dairy|Milk"
    assert coord.state.lists["rewe"].items[0].name == "Milk"


async def test_update_item_by_key(coord: GroceryCoordinator):
    coord.async_add_item("rewe", "Milk", category="Dairy")
    updated = coord.async_update_item("rewe", "Dairy", "Milk", new_name="Whole Milk")
    assert updated is not None
    assert coord.state.lists["rewe"].items[0].name == "Whole Milk"


async def test_set_checked_and_clear(coord: GroceryCoordinator):
    coord.async_add_item("rewe", "Milk")
    coord.async_set_checked("rewe", None, "Milk", True)
    cleared = coord.async_clear_checked("rewe")
    assert "|Milk" in cleared
    assert coord.state.lists["rewe"].items == []


async def test_delete_item(coord: GroceryCoordinator):
    coord.async_add_item("rewe", "Milk")
    assert coord.async_delete_item("rewe", None, "Milk") is True
    assert coord.state.lists["rewe"].items == []


async def test_restore_archived(coord: GroceryCoordinator):
    coord.async_add_item("rewe", "Milk", category="Dairy")
    coord.async_set_checked("rewe", "Dairy", "Milk", True)
    coord.async_clear_checked("rewe")
    restored = coord.async_restore_archived("rewe", "Dairy", "Milk")
    assert restored is not None
    assert coord.state.lists["rewe"].items[0].name == "Milk"
    assert coord.state.lists["rewe"].items[0].checked is False


async def test_undo_redo(coord: GroceryCoordinator):
    coord.async_add_item("rewe", "Milk")
    coord.async_undo()
    assert coord.state.lists["rewe"].items == []
    coord.async_redo()
    assert coord.state.lists["rewe"].items[0].name == "Milk"


async def test_snapshot_shape(coord: GroceryCoordinator):
    coord.async_add_item("rewe", "Milk", category="Dairy")
    snap = coord.snapshot()
    assert snap["identity"] == "kitchen-pi"
    assert snap["lists"][0]["slug"] == "rewe"
    assert "Dairy" in snap["categories"]
    item0 = snap["lists"][0]["items"][0]
    assert set(item0) == {"name", "category", "qty", "checked"}
