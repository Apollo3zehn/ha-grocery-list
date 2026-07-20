"""Tests for GroceryCoordinator mutation + undo/redo logic (PLAN §5, §6).

These exercise the git-independent behavior: item/category mutations, the op-log
recording, clear-checked, and per-identity undo/redo round-trips. We construct
the coordinator directly with the real ``hass`` fixture but do NOT call
``async_setup`` (which performs git I/O); instead we drive the in-memory model
and assert on state + op-log + sync-state transitions.

The debounce push timer is armed via ``async_call_later``; we assert the
sync-state flips to PENDING rather than waiting for the timer to fire.
"""

from __future__ import annotations

import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.grocery_list.const import (
    CONF_AUTH_METHOD,
    CONF_BRANCH,
    CONF_IDENTITY,
    CONF_REPO_URL,
    DOMAIN,
    SYNC_PENDING,
)
from custom_components.grocery_list.coordinator import GroceryCoordinator


@pytest.fixture
async def coordinator(hass: HomeAssistant) -> GroceryCoordinator:
    """Build a coordinator with a minimal fake config entry (no git setup)."""
    entry = ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="kitchen-pi",
        data={
            CONF_IDENTITY: "kitchen-pi",
            CONF_AUTH_METHOD: "https",
            CONF_REPO_URL: "https://example.com/x/y.git",
            CONF_BRANCH: "main",
        },
        source="user",
        options={},
        unique_id="y#main",
        discovery_keys=None,
        subentries_data=None,
    )
    return GroceryCoordinator(hass, entry)


async def test_add_item_records_op_and_pending(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item(
        "rewe", "Tomatoes", qty_value=2, qty_unit="pcs"
    )
    assert item.added_by == "kitchen-pi"
    assert item.qty is not None and item.qty.value == 2
    state = coordinator.state.lists["rewe"]
    assert item.id in state.items
    assert len(coordinator.state.oplog.ops) == 1
    assert coordinator.sync_state == SYNC_PENDING


async def test_add_item_without_qty(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item("rewe", "Milk")
    assert item.qty is None


async def test_update_item_changes_fields(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item("rewe", "Tomatoes")
    updated = coordinator.async_update_item(
        "rewe", item.id, name="Cherry Tomatoes", qty_value=3, qty_unit="pcs"
    )
    assert updated is not None
    assert updated.name == "Cherry Tomatoes"
    assert updated.qty.value == 3


async def test_update_item_missing_returns_none(coordinator: GroceryCoordinator):
    assert coordinator.async_update_item("rewe", "nope", name="X") is None


async def test_set_checked_sets_ts(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item("rewe", "Tomatoes")
    checked = coordinator.async_set_checked("rewe", item.id, True)
    assert checked.checked is True
    assert checked.checked_ts is not None
    unchecked = coordinator.async_set_checked("rewe", item.id, False)
    assert unchecked.checked is False
    assert unchecked.checked_ts is None


async def test_delete_item_leaves_tombstone(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item("rewe", "Tomatoes")
    assert coordinator.async_delete_item("rewe", item.id) is True
    state = coordinator.state.lists["rewe"]
    assert item.id not in state.items
    assert item.id in state.tombstones


async def test_clear_checked_archives_all_checked(coordinator: GroceryCoordinator):
    a = coordinator.async_add_item("rewe", "A")
    b = coordinator.async_add_item("rewe", "B")
    coordinator.async_add_item("rewe", "C")
    coordinator.async_set_checked("rewe", a.id, True)
    coordinator.async_set_checked("rewe", b.id, True)
    cleared = coordinator.async_clear_checked("rewe")
    assert set(cleared) == {a.id, b.id}
    state = coordinator.state.lists["rewe"]
    assert a.id in state.tombstones and state.tombstones[a.id].reason == "cleared"
    assert len(state.items) == 1  # only C remains
    # Cleared items are appended to the browsable archive.
    archive = coordinator.state.archives["rewe"]
    assert {e.item.id for e in archive} == {a.id, b.id}
    assert all(e.reason == "cleared" for e in archive)


async def test_category_crud(coordinator: GroceryCoordinator):
    cat = coordinator.async_create_category({"en": "Vegetables"})
    assert cat.id in coordinator.state.categories.categories
    updated = coordinator.async_update_category(cat.id, icon="mdi:carrot")
    assert updated.icon == "mdi:carrot"
    assert coordinator.async_delete_category(cat.id) is True
    assert cat.id not in coordinator.state.categories.categories


async def test_delete_category_uncategorizes_items(coordinator: GroceryCoordinator):
    cat = coordinator.async_create_category({"en": "Veg"})
    item = coordinator.async_add_item("rewe", "Tomatoes", category=cat.id)
    coordinator.async_delete_category(cat.id)
    assert coordinator.state.lists["rewe"].items[item.id].category is None


async def test_undo_add_removes_item(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item("rewe", "Tomatoes")
    assert coordinator.can_undo is True
    assert coordinator.async_undo() is True
    # Undo of an add => item removed.
    assert item.id not in coordinator.state.lists["rewe"].items
    assert coordinator.can_redo is True


async def test_redo_readds_item(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item("rewe", "Tomatoes")
    coordinator.async_undo()
    assert coordinator.async_redo() is True
    assert item.id in coordinator.state.lists["rewe"].items


async def test_undo_delete_restores_item(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item("rewe", "Tomatoes")
    coordinator.async_delete_item("rewe", item.id)
    assert coordinator.async_undo() is True
    # Undo of a delete => item restored.
    assert item.id in coordinator.state.lists["rewe"].items


async def test_undo_per_identity_nothing_to_undo(coordinator: GroceryCoordinator):
    assert coordinator.can_undo is False
    assert coordinator.async_undo() is False


async def test_undo_update_reverts_fields(coordinator: GroceryCoordinator):
    item = coordinator.async_add_item("rewe", "Tomatoes")
    coordinator.async_update_item("rewe", item.id, name="Changed")
    coordinator.async_undo()
    assert coordinator.state.lists["rewe"].items[item.id].name == "Tomatoes"


async def test_create_list_records_op_and_switch(coordinator: GroceryCoordinator):
    state = coordinator.async_create_list("Weekend BBQ")
    assert state.slug == "weekend-bbq"
    assert state.title == "Weekend BBQ"
    assert "weekend-bbq" in coordinator.state.lists
    assert len(coordinator.state.oplog.ops) == 1
    assert coordinator.sync_state == SYNC_PENDING


async def test_create_list_unique_slug(coordinator: GroceryCoordinator):
    a = coordinator.async_create_list("Groceries")
    b = coordinator.async_create_list("Groceries")
    assert a.slug == "groceries"
    assert b.slug == "groceries-2"


async def test_create_list_avoids_tombstoned_slug(coordinator: GroceryCoordinator):
    coordinator.async_create_list("Groceries")
    coordinator.async_delete_list("groceries")
    # A new list with the same title must not reuse the tombstoned slug, or the
    # tombstone would suppress it on merge.
    again = coordinator.async_create_list("Groceries")
    assert again.slug != "groceries"


async def test_rename_list_changes_title(coordinator: GroceryCoordinator):
    coordinator.async_create_list("Old")
    renamed = coordinator.async_rename_list("old", "New Name")
    assert renamed is not None
    assert renamed.title == "New Name"
    assert coordinator.state.lists["old"].title == "New Name"


async def test_rename_missing_list_returns_none(coordinator: GroceryCoordinator):
    assert coordinator.async_rename_list("nope", "X") is None


async def test_delete_list_leaves_list_tombstone(coordinator: GroceryCoordinator):
    coordinator.async_create_list("Trip")
    coordinator.async_add_item("trip", "Water")
    assert coordinator.async_delete_list("trip") is True
    assert "trip" not in coordinator.state.lists
    assert "trip" in coordinator.state.list_tombstones


async def test_delete_missing_list_returns_false(coordinator: GroceryCoordinator):
    assert coordinator.async_delete_list("nope") is False


async def test_delete_list_excluded_from_snapshot(coordinator: GroceryCoordinator):
    coordinator.async_create_list("Keep")
    coordinator.async_create_list("Drop")
    coordinator.async_delete_list("drop")
    slugs = {l["slug"] for l in coordinator.snapshot()["lists"]}
    assert "keep" in slugs
    assert "drop" not in slugs


async def test_undo_delete_list_restores_items(coordinator: GroceryCoordinator):
    coordinator.async_create_list("Trip")
    item = coordinator.async_add_item("trip", "Water")
    coordinator.async_delete_list("trip")
    assert coordinator.async_undo() is True
    # Undo of a list delete => list + its items restored, tombstone cleared.
    assert "trip" in coordinator.state.lists
    assert item.id in coordinator.state.lists["trip"].items
    assert "trip" not in coordinator.state.list_tombstones


async def test_undo_create_list_removes_it(coordinator: GroceryCoordinator):
    coordinator.async_create_list("Ephemeral")
    assert coordinator.async_undo() is True
    # Undo of a create => list removed and a list-level tombstone left.
    assert "ephemeral" not in coordinator.state.lists
    assert "ephemeral" in coordinator.state.list_tombstones


async def test_purge_removes_old_and_leaves_recent(
    coordinator: GroceryCoordinator,
):
    from custom_components.grocery_list.models import (
        ArchivedItem,
        Item,
        ListState,
    )

    state = coordinator.state.lists.setdefault(
        "rewe", ListState(slug="rewe", title="Rewe")
    )

    def _archived(iid, arch_ts):
        return ArchivedItem(
            item=Item(
                id=iid,
                name=iid,
                added_by="kitchen-pi",
                created_ts=arch_ts,
                updated_ts=arch_ts,
                checked=True,
                checked_ts=arch_ts,
            ),
            archived_ts=arch_ts,
            reason="cleared",
        )

    old = _archived("old", "2000-01-01T00:00:00Z")
    recent = _archived("recent", "2999-01-01T00:00:00Z")
    coordinator.state.archives["rewe"] = [old, recent]

    purged = coordinator.async_purge_archives()
    assert purged == 1
    remaining = coordinator.state.archives["rewe"]
    assert {e.item.id for e in remaining} == {"recent"}
    # Purged item gets a purged tombstone so it can't resurrect.
    assert state.tombstones["old"].reason == "purged"


async def test_purge_prunes_empty_slug(coordinator: GroceryCoordinator):
    from custom_components.grocery_list.models import ArchivedItem, Item

    coordinator.state.archives["rewe"] = [
        ArchivedItem(
            item=Item(
                id="old",
                name="old",
                added_by="kitchen-pi",
                created_ts="2000-01-01T00:00:00Z",
                updated_ts="2000-01-01T00:00:00Z",
                checked=True,
                checked_ts="2000-01-01T00:00:00Z",
            ),
            archived_ts="2000-01-01T00:00:00Z",
            reason="cleared",
        )
    ]
    coordinator.async_purge_archives()
    # Slug with no remaining entries is dropped so no empty file is written.
    assert "rewe" not in coordinator.state.archives


async def test_purge_disabled_when_retention_zero(
    hass: HomeAssistant,
):
    from custom_components.grocery_list.models import ArchivedItem, Item

    entry = ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="kitchen-pi",
        data={
            CONF_IDENTITY: "kitchen-pi",
            CONF_AUTH_METHOD: "https",
            CONF_REPO_URL: "https://example.com/x/y.git",
            CONF_BRANCH: "main",
        },
        source="user",
        options={"archive_retention_days": 0},
        unique_id="y#main",
        discovery_keys=None,
        subentries_data=None,
    )
    coordinator = GroceryCoordinator(hass, entry)
    coordinator.state.archives["rewe"] = [
        ArchivedItem(
            item=Item(
                id="old",
                name="old",
                added_by="kitchen-pi",
                created_ts="2000-01-01T00:00:00Z",
                updated_ts="2000-01-01T00:00:00Z",
                checked=True,
                checked_ts="2000-01-01T00:00:00Z",
            ),
            archived_ts="2000-01-01T00:00:00Z",
            reason="cleared",
        )
    ]
    assert coordinator.async_purge_archives() == 0
    assert len(coordinator.state.archives["rewe"]) == 1
