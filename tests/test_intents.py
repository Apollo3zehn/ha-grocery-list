"""Tests for the Grocery List intent handlers.

These intents are what expose grocery operations to Assist and, via
``AssistAPI``, to LLM/MCP clients token-free. We register the handlers, then
drive them through ``intent.async_handle`` exactly as the conversation/LLM
layer would, asserting both the coordinator state changed and that the response
carries useful speech + structured ``speech_slots``.

Handlers are backed by a directly-constructed coordinator (no git), mirroring
``test_services.py``. Item identity is ``(category, name)``; list resolution is
by human title/slug, case-insensitive, with sole-list defaulting.
"""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from custom_components.grocery_list import intents
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
async def setup_intents(hass: HomeAssistant):
    """Register intents + a single coordinator; yield the coordinator.

    The coordinator arms a debounce timer on every mutation; we cancel it in
    teardown via ``async_shutdown`` so the stricter phacc harness doesn't fail
    on a lingering timer. ``CONF_SYNC_ENABLED=False`` keeps us on the local
    (git-free) write path.
    """
    entry = _make_entry(hass, "kitchen-pi")
    coordinator = GroceryCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    intents.async_setup_intents(hass)
    yield coordinator
    await coordinator.async_shutdown()


async def _handle(
    hass: HomeAssistant, intent_type: str, slots: dict | None = None
) -> intent.IntentResponse:
    """Invoke an intent the way the conversation/LLM layer does.

    ``slots`` is given as plain ``{name: value}`` and wrapped into the
    ``{name: {"value": value}}`` shape Home Assistant expects.
    """
    wrapped = {k: {"value": v} for k, v in (slots or {}).items()}
    return await intent.async_handle(
        hass, DOMAIN, intent_type, slots=wrapped, assistant="conversation"
    )


# ---------------------------------------------------------------------------
# platforms=None (LLM exposure) guarantee
# ---------------------------------------------------------------------------


async def test_all_handlers_platforms_none(hass: HomeAssistant, setup_intents):
    """Every handler must set platforms=None so AssistAPI exposes it as a tool.

    AssistAPI drops intent handlers whose platforms don't intersect the
    exposed-entity domains; grocery lists aren't entities, so None is required.
    """
    for cls in intents._HANDLER_CLASSES:
        assert cls.platforms is None


async def test_handlers_registered(hass: HomeAssistant, setup_intents):
    """All 10 grocery intents are discoverable via the intent registry."""
    registered = {h.intent_type for h in intent.async_get(hass)}
    for cls in intents._HANDLER_CLASSES:
        assert cls.intent_type in registered


# ---------------------------------------------------------------------------
# Read intents
# ---------------------------------------------------------------------------


async def test_get_lists(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    coord.async_add_item("groceries", "Milk")
    coord.async_add_item("groceries", "Bread")
    coord.async_set_checked("groceries", None, "Bread", True)

    resp = await _handle(hass, intents.INTENT_GET_LISTS)
    assert resp.response_type is intent.IntentResponseType.QUERY_ANSWER
    lists = resp.speech_slots["lists"]
    assert len(lists) == 1
    assert lists[0]["name"] == "Groceries"
    assert lists[0]["total_items"] == 2
    assert lists[0]["unchecked_items"] == 1


async def test_get_items_sole_list_default(hass: HomeAssistant, setup_intents):
    """list_name may be omitted when exactly one list exists."""
    coord = setup_intents
    coord.async_create_list("Groceries")
    coord.async_add_item("groceries", "Milk")

    resp = await _handle(hass, intents.INTENT_GET_ITEMS)
    assert resp.response_type is intent.IntentResponseType.QUERY_ANSWER
    assert resp.speech_slots["list"] == "Groceries"
    names = [it["name"] for it in resp.speech_slots["items"]]
    assert names == ["Milk"]


async def test_get_items_only_unchecked(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    coord.async_add_item("groceries", "Milk")
    coord.async_add_item("groceries", "Bread")
    coord.async_set_checked("groceries", None, "Bread", True)

    resp = await _handle(
        hass, intents.INTENT_GET_ITEMS, {"only_unchecked": True}
    )
    names = [it["name"] for it in resp.speech_slots["items"]]
    assert names == ["Milk"]


# ---------------------------------------------------------------------------
# Mutation intents
# ---------------------------------------------------------------------------


async def test_add_item(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")

    resp = await _handle(
        hass,
        intents.INTENT_ADD_ITEM,
        {"name": "Milk", "qty_value": 2, "qty_unit": "l", "category": "Dairy"},
    )
    assert resp.response_type is intent.IntentResponseType.ACTION_DONE
    items = coord.state.lists["groceries"].items
    assert len(items) == 1
    assert items[0].name == "Milk"
    assert items[0].category == "Dairy"
    assert items[0].qty.value == 2
    assert items[0].qty.unit == "l"
    assert resp.speech_slots["added"]["name"] == "Milk"


async def test_check_and_uncheck_item(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    coord.async_add_item("groceries", "Milk")

    await _handle(hass, intents.INTENT_CHECK_ITEM, {"name": "Milk"})
    assert coord.state.lists["groceries"].items[0].checked is True

    await _handle(hass, intents.INTENT_UNCHECK_ITEM, {"name": "Milk"})
    assert coord.state.lists["groceries"].items[0].checked is False


async def test_remove_item(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    coord.async_add_item("groceries", "Milk")

    resp = await _handle(hass, intents.INTENT_REMOVE_ITEM, {"name": "Milk"})
    assert coord.state.lists["groceries"].items == []
    assert resp.speech_slots["removed"] == "Milk"


async def test_clear_checked(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    coord.async_add_item("groceries", "Milk")
    coord.async_add_item("groceries", "Bread")
    coord.async_set_checked("groceries", None, "Milk", True)

    resp = await _handle(hass, intents.INTENT_CLEAR_CHECKED)
    assert resp.speech_slots["cleared_count"] == 1
    remaining = [it.name for it in coord.state.lists["groceries"].items]
    assert remaining == ["Bread"]


async def test_create_list(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    resp = await _handle(
        hass, intents.INTENT_CREATE_LIST, {"name": "Hardware Store"}
    )
    assert resp.speech_slots["created"] == "Hardware Store"
    titles = {g.title for g in coord.state.lists.values()}
    assert "Hardware Store" in titles


async def test_rename_list(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    resp = await _handle(
        hass,
        intents.INTENT_RENAME_LIST,
        {"list_name": "Groceries", "new_name": "Weekly Shop"},
    )
    assert resp.speech_slots["renamed_to"] == "Weekly Shop"
    assert coord.state.lists["groceries"].title == "Weekly Shop"


async def test_delete_list(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    resp = await _handle(
        hass, intents.INTENT_DELETE_LIST, {"list_name": "Groceries"}
    )
    assert resp.speech_slots["deleted"] == "Groceries"
    assert "groceries" not in coord.state.lists


# ---------------------------------------------------------------------------
# Resolution: list matching, item matching, error surfaces
# ---------------------------------------------------------------------------


async def test_resolve_list_by_slug_case_insensitive(
    hass: HomeAssistant, setup_intents
):
    coord = setup_intents
    coord.async_create_list("Groceries")  # slug 'groceries'
    resp = await _handle(
        hass, intents.INTENT_ADD_ITEM, {"name": "Milk", "list_name": "GROCERIES"}
    )
    assert resp.speech_slots["list"] == "Groceries"
    assert len(coord.state.lists["groceries"].items) == 1


async def test_ambiguous_list_requires_name(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    coord.async_create_list("Hardware")
    with pytest.raises(intent.IntentHandleError, match="Multiple lists exist"):
        await _handle(hass, intents.INTENT_GET_ITEMS)


async def test_unknown_list_lists_available(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    with pytest.raises(intent.IntentHandleError, match="No list named 'Nope'"):
        await _handle(
            hass, intents.INTENT_GET_ITEMS, {"list_name": "Nope"}
        )


async def test_item_not_found(hass: HomeAssistant, setup_intents):
    coord = setup_intents
    coord.async_create_list("Groceries")
    with pytest.raises(intent.IntentHandleError, match="No item 'Ghost'"):
        await _handle(
            hass, intents.INTENT_CHECK_ITEM, {"name": "Ghost"}
        )


async def test_ambiguous_item_requires_category(
    hass: HomeAssistant, setup_intents
):
    """Same name in two categories forces the LLM to specify a category."""
    coord = setup_intents
    coord.async_create_list("Groceries")
    coord.async_add_item("groceries", "Milk", category="Dairy")
    coord.async_add_item("groceries", "Milk", category="Vegan")
    with pytest.raises(intent.IntentHandleError, match="specify category"):
        await _handle(hass, intents.INTENT_CHECK_ITEM, {"name": "Milk"})
    # Disambiguated by category, it succeeds.
    await _handle(
        hass,
        intents.INTENT_CHECK_ITEM,
        {"name": "Milk", "category": "Vegan"},
    )
    vegan = coord.state.lists["groceries"].item_by_key("Vegan", "Milk")
    assert vegan.checked is True


async def test_no_lists_get_items_errors(hass: HomeAssistant, setup_intents):
    """With zero lists, a read intent explains none exist."""
    with pytest.raises(intent.IntentHandleError, match="No grocery lists exist"):
        await _handle(hass, intents.INTENT_GET_ITEMS)


async def test_add_item_updates_existing_quantity(
    hass: HomeAssistant, setup_intents
):
    """Adding an existing (category,name) replaces it (quantity update)."""
    coord = setup_intents
    coord.async_create_list("Groceries")
    await _handle(
        hass, intents.INTENT_ADD_ITEM, {"name": "Milk", "qty_value": 1}
    )
    await _handle(
        hass, intents.INTENT_ADD_ITEM, {"name": "Milk", "qty_value": 3}
    )
    items = coord.state.lists["groceries"].items
    assert len(items) == 1
    assert items[0].qty.value == 3
