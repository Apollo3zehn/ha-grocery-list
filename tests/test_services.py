"""Tests for the Grocery List domain services (PLAN §9).

Services expose the same high-level actions as the websocket API to automations
and voice assistants. We register services against a directly-constructed
coordinator (no git) and call them through ``hass.services.async_call``,
asserting the coordinator state changed and that entry resolution (explicit vs.
sole-entry default vs. ambiguous) behaves correctly.
"""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.grocery_list import services
from custom_components.grocery_list.const import (
    CONF_AUTH_METHOD,
    CONF_BRANCH,
    CONF_IDENTITY,
    CONF_REPO_URL,
    CONF_SYNC_ENABLED,
    DOMAIN,
)
from custom_components.grocery_list.coordinator import GroceryCoordinator


def _make_entry(hass: HomeAssistant, identity: str) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=identity,
        data={
            CONF_IDENTITY: identity,
            CONF_AUTH_METHOD: "https",
            CONF_REPO_URL: f"https://example.com/x/{identity}.git",
            CONF_BRANCH: "main",
            CONF_SYNC_ENABLED: False,
        },
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def setup_services(hass: HomeAssistant):
    """Register services + a single coordinator; yield (entry_id, coordinator).

    Teardown cancels the coordinator's debounce timer via ``async_shutdown`` so
    the phacc harness doesn't fail on a lingering timer; ``CONF_SYNC_ENABLED``
    is False to stay on the local write path.
    """
    entry = _make_entry(hass, "kitchen-pi")
    coordinator = GroceryCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    services.async_register(hass)
    yield entry.entry_id, coordinator
    await coordinator.async_shutdown()


async def test_add_item_service(hass: HomeAssistant, setup_services):
    _entry_id, coordinator = setup_services
    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {"slug": "rewe", "name": "Tomatoes", "qty_value": 2, "qty_unit": "pcs"},
        blocking=True,
    )
    items = coordinator.state.lists["rewe"].items
    assert len(items) == 1
    assert items[0].name == "Tomatoes"
    assert items[0].qty.value == 2


async def test_clear_checked_service(hass: HomeAssistant, setup_services):
    _entry_id, coordinator = setup_services
    coordinator.async_add_item("rewe", "A")
    coordinator.async_set_checked("rewe", None, "A", True)
    await hass.services.async_call(
        DOMAIN, "clear_checked", {"slug": "rewe"}, blocking=True
    )
    assert coordinator.state.lists["rewe"].items == []


async def test_undo_redo_services(hass: HomeAssistant, setup_services):
    _entry_id, coordinator = setup_services
    coordinator.async_add_item("rewe", "Bread")
    await hass.services.async_call(DOMAIN, "undo", {}, blocking=True)
    assert coordinator.state.lists["rewe"].items == []
    await hass.services.async_call(DOMAIN, "redo", {}, blocking=True)
    assert coordinator.state.lists["rewe"].items[0].name == "Bread"


async def test_default_entry_resolution(hass: HomeAssistant, setup_services):
    """With a single entry, omitting entry_id resolves to it."""
    _entry_id, coordinator = setup_services
    await hass.services.async_call(
        DOMAIN, "add_item", {"slug": "rewe", "name": "X"}, blocking=True
    )
    assert len(coordinator.state.lists["rewe"].items) == 1


async def test_explicit_entry_id(hass: HomeAssistant, setup_services):
    entry_id, coordinator = setup_services
    await hass.services.async_call(
        DOMAIN,
        "add_item",
        {"entry_id": entry_id, "slug": "rewe", "name": "X"},
        blocking=True,
    )
    assert len(coordinator.state.lists["rewe"].items) == 1


async def test_ambiguous_entry_raises(hass: HomeAssistant):
    """With two entries and no entry_id, the service errors."""
    e1 = _make_entry(hass, "kitchen-pi")
    e2 = _make_entry(hass, "living-room")
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][e1.entry_id] = GroceryCoordinator(hass, e1)
    hass.data[DOMAIN][e2.entry_id] = GroceryCoordinator(hass, e2)
    services.async_register(hass)
    with pytest.raises(HomeAssistantError, match="specify entry_id"):
        await hass.services.async_call(
            DOMAIN, "add_item", {"slug": "rewe", "name": "X"}, blocking=True
        )


async def test_unknown_entry_raises(hass: HomeAssistant, setup_services):
    with pytest.raises(HomeAssistantError, match="No grocery_list entry"):
        await hass.services.async_call(
            DOMAIN,
            "add_item",
            {"entry_id": "nope", "slug": "rewe", "name": "X"},
            blocking=True,
        )
