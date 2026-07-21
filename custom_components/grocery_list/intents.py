"""Intent handlers for the Grocery List integration.

These intents expose grocery-list operations to Home Assistant's Assist
pipeline and, crucially, to any LLM/MCP client. Home Assistant's built-in
``AssistAPI`` automatically wraps every registered intent into an LLM tool and
serves it token-free at ``/api/mcp/assist`` — so registering intents here is
what lets a conversation agent (or an MCP client) say "add milk to the shopping
list", "what's on the grocery list?", "clear the checked items", etc., with zero
extra user configuration.

WHY intents (vs a custom ``llm.API``): contributing intents merges our tools
into whatever assistant the user already configured and reaches the token-free
``/api/mcp/assist`` endpoint. A full custom ``llm.API`` would instead live at
``/api/mcp/<id>`` behind an admin token with manual selection.

Every handler is a thin wrapper over :class:`GroceryCoordinator` — the same
methods the websocket API and services call — so an LLM action, a card action,
and a service call are fully equivalent (op recorded, model updated, listeners
notified, debounced push/write armed).

IMPORTANT — ``platforms = None``: ``AssistAPI`` filters intent handlers by the
domains of *exposed entities*, keeping a handler only when
``handler.platforms is None or handler.platforms & exposed_domains``. Grocery
lists are NOT entities, so every handler here sets ``platforms = None`` to
remain exposed as an LLM tool regardless of which entities the user exposed.

List identity for the LLM: handlers accept a human ``list_name`` (matched
against each list's title or slug, case-insensitively) rather than an opaque
slug. When exactly one list exists, ``list_name`` may be omitted. Item identity
is ``(category, name)``; when ``category`` is omitted we resolve by name if it
is unambiguous within the list.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, intent

from .const import DOMAIN
from .coordinator import GroceryCoordinator
from .models import GroceryList, Item

# Intent type names. Prefixed with ``GroceryList`` so they read clearly as LLM
# tool names and never collide with built-in intents.
INTENT_GET_LISTS = "GroceryListGetLists"
INTENT_GET_ITEMS = "GroceryListGetItems"
INTENT_ADD_ITEM = "GroceryListAddItem"
INTENT_CHECK_ITEM = "GroceryListCheckItem"
INTENT_UNCHECK_ITEM = "GroceryListUncheckItem"
INTENT_REMOVE_ITEM = "GroceryListRemoveItem"
INTENT_CLEAR_CHECKED = "GroceryListClearChecked"
INTENT_CREATE_LIST = "GroceryListCreateList"
INTENT_RENAME_LIST = "GroceryListRenameList"
INTENT_DELETE_LIST = "GroceryListDeleteList"


# ---------------------------------------------------------------------------
# Resolution helpers
# ---------------------------------------------------------------------------


def _all_coordinators(hass: HomeAssistant) -> list[GroceryCoordinator]:
    """Return every loaded Grocery List coordinator (one per config entry)."""
    return list(hass.data.get(DOMAIN, {}).values())


def _iter_lists(
    hass: HomeAssistant,
) -> list[tuple[GroceryCoordinator, str, GroceryList]]:
    """Return ``(coordinator, slug, list)`` for every list across all entries."""
    out: list[tuple[GroceryCoordinator, str, GroceryList]] = []
    for coord in _all_coordinators(hass):
        for slug, glist in coord.state.lists.items():
            out.append((coord, slug, glist))
    return out


def _default_coordinator(hass: HomeAssistant) -> GroceryCoordinator:
    """Return the sole coordinator, or raise if there are zero or several."""
    coords = _all_coordinators(hass)
    if not coords:
        raise intent.IntentHandleError(
            "Grocery List is not configured.", "not_configured"
        )
    if len(coords) == 1:
        return coords[0]
    raise intent.IntentHandleError(
        "Multiple Grocery List instances are loaded; cannot choose one "
        "automatically.",
        "ambiguous_instance",
    )


def _resolve_list(
    hass: HomeAssistant, list_name: str | None
) -> tuple[GroceryCoordinator, str, GroceryList]:
    """Resolve a human list name to ``(coordinator, slug, list)``.

    Matches ``list_name`` against each list's title or slug case-insensitively.
    When ``list_name`` is omitted and exactly one list exists, that list is
    used. Ambiguity or a miss raises an ``IntentHandleError`` whose message
    lists the available names so the LLM can correct itself.
    """
    all_lists = _iter_lists(hass)
    if not all_lists:
        raise intent.IntentHandleError(
            "No grocery lists exist yet. Create one with GroceryListCreateList.",
            "no_lists",
        )
    if list_name is None:
        if len(all_lists) == 1:
            return all_lists[0]
        titles = ", ".join(sorted(g.title for _, _, g in all_lists))
        raise intent.IntentHandleError(
            f"Multiple lists exist; specify list_name. Available: {titles}",
            "ambiguous_list",
        )
    target = list_name.strip().lower()
    matches = [
        (c, s, g)
        for c, s, g in all_lists
        if g.title.lower() == target or s.lower() == target
    ]
    if not matches:
        titles = ", ".join(sorted(g.title for _, _, g in all_lists))
        raise intent.IntentHandleError(
            f"No list named '{list_name}'. Available: {titles}", "list_not_found"
        )
    if len(matches) > 1:
        raise intent.IntentHandleError(
            f"More than one list is named '{list_name}'; rename to "
            "disambiguate.",
            "ambiguous_list",
        )
    return matches[0]


def _resolve_item(glist: GroceryList, name: str, category: str | None) -> Item:
    """Find an item by name (+ optional category) within a list.

    Matching is case-insensitive. When ``category`` is given it must also
    match. When it is omitted and several items share the name across
    categories, the ambiguity is surfaced so the LLM can supply a category.
    """
    tname = name.strip().lower()
    tcat = category.strip().lower() if category else None
    matches = [
        it
        for it in glist.items
        if it.name.lower() == tname
        and (tcat is None or (it.category or "").lower() == tcat)
    ]
    if not matches:
        raise intent.IntentHandleError(
            f"No item '{name}' found on list '{glist.title}'.", "item_not_found"
        )
    if len(matches) > 1:
        cats = ", ".join(
            sorted(m.category or "(uncategorized)" for m in matches)
        )
        raise intent.IntentHandleError(
            f"Several items named '{name}' exist (categories: {cats}); "
            "specify category.",
            "ambiguous_item",
        )
    return matches[0]


def _item_view(item: Item) -> dict[str, Any]:
    """Compact JSON view of an item for speech-slot payloads."""
    view: dict[str, Any] = {
        "name": item.name,
        "category": item.category,
        "checked": item.checked,
    }
    if item.qty is not None:
        view["qty"] = {"value": item.qty.value, "unit": item.qty.unit}
    return view


def _slot(slots: dict, key: str) -> Any | None:
    """Return the value of an optional validated slot, or ``None``."""
    entry = slots.get(key)
    if entry is None:
        return None
    return entry.get("value")


# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------


class _GroceryIntentHandler(intent.IntentHandler):
    """Base: expose to the LLM regardless of exposed-entity domains.

    ``platforms = None`` is essential — see the module docstring. Without it,
    ``AssistAPI`` would drop these handlers because no grocery *entity* is
    exposed, and the tools would never reach the LLM/MCP surface.
    """

    platforms = None

    @callback
    def _query_response(
        self, intent_obj: intent.Intent, speech: str, slots: dict[str, Any]
    ) -> intent.IntentResponse:
        """Build a QUERY_ANSWER response carrying speech + structured slots."""
        response = intent_obj.create_response()
        response.response_type = intent.IntentResponseType.QUERY_ANSWER
        response.async_set_speech(speech)
        response.async_set_speech_slots(slots)
        return response

    @callback
    def _action_response(
        self, intent_obj: intent.Intent, speech: str, slots: dict[str, Any]
    ) -> intent.IntentResponse:
        """Build an ACTION_DONE response carrying speech + structured slots."""
        response = intent_obj.create_response()
        response.async_set_speech(speech)
        response.async_set_speech_slots(slots)
        return response


class GetListsIntentHandler(_GroceryIntentHandler):
    """List all grocery lists with item counts."""

    intent_type = INTENT_GET_LISTS
    description = (
        "List all grocery lists with their names and item counts. Call this "
        "to discover available lists before referring to one by name."
    )
    slot_schema: dict = {}

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        lists = []
        for _c, _s, glist in _iter_lists(intent_obj.hass):
            unchecked = sum(1 for it in glist.items if not it.checked)
            lists.append(
                {
                    "name": glist.title,
                    "total_items": len(glist.items),
                    "unchecked_items": unchecked,
                }
            )
        if not lists:
            speech = "There are no grocery lists yet."
        else:
            speech = "; ".join(
                f"{ls['name']} ({ls['unchecked_items']} to buy, "
                f"{ls['total_items']} total)"
                for ls in lists
            )
        return self._query_response(intent_obj, speech, {"lists": lists})


class GetItemsIntentHandler(_GroceryIntentHandler):
    """Get the items on a grocery list."""

    intent_type = INTENT_GET_ITEMS
    description = (
        "Get the items on a grocery list. Omit list_name if only one list "
        "exists. Use this to answer what is on the list or what needs buying."
    )
    slot_schema = {
        vol.Optional("list_name"): cv.string,
        vol.Optional("only_unchecked"): cv.boolean,
    }

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        slots = self.async_validate_slots(intent_obj.slots)
        _c, _s, glist = _resolve_list(intent_obj.hass, _slot(slots, "list_name"))
        only_unchecked = bool(_slot(slots, "only_unchecked") or False)
        items = [
            _item_view(it)
            for it in glist.items
            if not (only_unchecked and it.checked)
        ]
        if not items:
            speech = f"The {glist.title} list is empty."
        else:
            names = ", ".join(it["name"] for it in items)
            speech = f"The {glist.title} list has: {names}."
        return self._query_response(
            intent_obj, speech, {"list": glist.title, "items": items}
        )


class AddItemIntentHandler(_GroceryIntentHandler):
    """Add an item to a grocery list (or update its quantity)."""

    intent_type = INTENT_ADD_ITEM
    description = (
        "Add an item to a grocery list (or update its quantity if it already "
        "exists). Omit list_name if only one list exists."
    )
    slot_schema = {
        vol.Required("name"): intent.non_empty_string,
        vol.Optional("list_name"): cv.string,
        vol.Optional("category"): cv.string,
        vol.Optional("qty_value"): vol.Coerce(float),
        vol.Optional("qty_unit"): cv.string,
    }

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        slots = self.async_validate_slots(intent_obj.slots)
        coord, slug, glist = _resolve_list(
            intent_obj.hass, _slot(slots, "list_name")
        )
        item = coord.async_add_item(
            slug,
            slots["name"]["value"].strip(),
            category=(_slot(slots, "category") or None),
            qty_value=_slot(slots, "qty_value"),
            qty_unit=_slot(slots, "qty_unit"),
        )
        return self._action_response(
            intent_obj,
            f"Added {item.name} to {glist.title}.",
            {"added": _item_view(item), "list": glist.title},
        )


class _SetCheckedIntentHandler(_GroceryIntentHandler):
    """Shared implementation for check/uncheck (distinct intent types)."""

    _checked = True

    slot_schema = {
        vol.Required("name"): intent.non_empty_string,
        vol.Optional("list_name"): cv.string,
        vol.Optional("category"): cv.string,
    }

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        slots = self.async_validate_slots(intent_obj.slots)
        coord, slug, glist = _resolve_list(
            intent_obj.hass, _slot(slots, "list_name")
        )
        item = _resolve_item(
            glist, slots["name"]["value"], _slot(slots, "category")
        )
        updated = coord.async_set_checked(
            slug, item.category, item.name, self._checked
        )
        assert updated is not None  # resolved above
        verb = "Checked off" if self._checked else "Unchecked"
        return self._action_response(
            intent_obj,
            f"{verb} {updated.name} on {glist.title}.",
            {"item": _item_view(updated), "list": glist.title},
        )


class CheckItemIntentHandler(_SetCheckedIntentHandler):
    """Mark an item as checked/bought."""

    intent_type = INTENT_CHECK_ITEM
    description = (
        "Mark an item as checked/bought on a grocery list. Omit list_name if "
        "only one list exists."
    )
    _checked = True


class UncheckItemIntentHandler(_SetCheckedIntentHandler):
    """Mark a checked item as not bought again."""

    intent_type = INTENT_UNCHECK_ITEM
    description = (
        "Mark a checked item as not bought again (uncheck it). Omit list_name "
        "if only one list exists."
    )
    _checked = False


class RemoveItemIntentHandler(_GroceryIntentHandler):
    """Remove an item from a grocery list entirely."""

    intent_type = INTENT_REMOVE_ITEM
    description = (
        "Remove an item from a grocery list entirely. Omit list_name if only "
        "one list exists."
    )
    slot_schema = {
        vol.Required("name"): intent.non_empty_string,
        vol.Optional("list_name"): cv.string,
        vol.Optional("category"): cv.string,
    }

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        slots = self.async_validate_slots(intent_obj.slots)
        coord, slug, glist = _resolve_list(
            intent_obj.hass, _slot(slots, "list_name")
        )
        item = _resolve_item(
            glist, slots["name"]["value"], _slot(slots, "category")
        )
        coord.async_delete_item(slug, item.category, item.name)
        return self._action_response(
            intent_obj,
            f"Removed {item.name} from {glist.title}.",
            {"removed": item.name, "list": glist.title},
        )


class ClearCheckedIntentHandler(_GroceryIntentHandler):
    """Remove all checked/bought items from a grocery list."""

    intent_type = INTENT_CLEAR_CHECKED
    description = (
        "Remove all checked/bought items from a grocery list (they are "
        "archived). Omit list_name if only one list exists."
    )
    slot_schema = {vol.Optional("list_name"): cv.string}

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        slots = self.async_validate_slots(intent_obj.slots)
        coord, slug, glist = _resolve_list(
            intent_obj.hass, _slot(slots, "list_name")
        )
        cleared = coord.async_clear_checked(slug)
        return self._action_response(
            intent_obj,
            f"Cleared {len(cleared)} checked item(s) from {glist.title}.",
            {"cleared_count": len(cleared), "list": glist.title},
        )


class CreateListIntentHandler(_GroceryIntentHandler):
    """Create a new, empty grocery list."""

    intent_type = INTENT_CREATE_LIST
    description = "Create a new, empty grocery list with the given name."
    slot_schema = {vol.Required("name"): intent.non_empty_string}

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        slots = self.async_validate_slots(intent_obj.slots)
        coord = _default_coordinator(intent_obj.hass)
        glist = coord.async_create_list(slots["name"]["value"].strip())
        return self._action_response(
            intent_obj,
            f"Created the {glist.title} list.",
            {"created": glist.title},
        )


class RenameListIntentHandler(_GroceryIntentHandler):
    """Rename an existing grocery list."""

    intent_type = INTENT_RENAME_LIST
    description = "Rename an existing grocery list."
    slot_schema = {
        vol.Required("list_name"): intent.non_empty_string,
        vol.Required("new_name"): intent.non_empty_string,
    }

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        slots = self.async_validate_slots(intent_obj.slots)
        coord, slug, _g = _resolve_list(
            intent_obj.hass, slots["list_name"]["value"]
        )
        state = coord.async_rename_list(slug, slots["new_name"]["value"].strip())
        assert state is not None
        return self._action_response(
            intent_obj,
            f"Renamed the list to {state.title}.",
            {"renamed_to": state.title},
        )


class DeleteListIntentHandler(_GroceryIntentHandler):
    """Delete an entire grocery list and all its items."""

    intent_type = INTENT_DELETE_LIST
    description = (
        "Delete an entire grocery list and all its items. This cannot be "
        "undone via these tools."
    )
    slot_schema = {vol.Required("list_name"): intent.non_empty_string}

    async def async_handle(
        self, intent_obj: intent.Intent
    ) -> intent.IntentResponse:
        slots = self.async_validate_slots(intent_obj.slots)
        coord, slug, glist = _resolve_list(
            intent_obj.hass, slots["list_name"]["value"]
        )
        title = glist.title
        coord.async_delete_list(slug)
        return self._action_response(
            intent_obj, f"Deleted the {title} list.", {"deleted": title}
        )


_HANDLER_CLASSES: tuple[type[_GroceryIntentHandler], ...] = (
    GetListsIntentHandler,
    GetItemsIntentHandler,
    AddItemIntentHandler,
    CheckItemIntentHandler,
    UncheckItemIntentHandler,
    RemoveItemIntentHandler,
    ClearCheckedIntentHandler,
    CreateListIntentHandler,
    RenameListIntentHandler,
    DeleteListIntentHandler,
)


@callback
def async_setup_intents(hass: HomeAssistant) -> None:
    """Register all Grocery List intent handlers (called once from setup).

    Intents are global (not per-entry); handlers resolve the target
    coordinator(s) from ``hass.data[DOMAIN]`` at call time, so registering once
    on the first config entry is sufficient. Registration is idempotent —
    re-registering the same intent type simply replaces the handler.
    """
    for cls in _HANDLER_CLASSES:
        intent.async_register(hass, cls())
