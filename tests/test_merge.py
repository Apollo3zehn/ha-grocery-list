"""Unit tests for the semantic 3-way merge engine.

Items are keyed by ``(category, name)``. Deletions are structural: an item in
``base`` that is absent (and unchanged on the surviving side) is dropped. There
are no tombstones or timestamps.
"""

from grocery_list.merge import merge
from grocery_list.models import GroceryList, Item, Quantity


def _list(*items: Item, title="Rewe", slug="rewe") -> GroceryList:
    return GroceryList(slug=slug, title=title, items=list(items))


def test_disjoint_additions_are_unioned():
    base = _list()
    ours = _list(Item(name="Milk"))
    theirs = _list(Item(name="Bread"))
    result = merge(base, ours, theirs)
    assert {it.name for it in result.items} == {"Milk", "Bread"}


def test_same_item_present_both_sides_merges_once():
    base = _list()
    ours = _list(Item(name="Milk"))
    theirs = _list(Item(name="Milk"))
    result = merge(base, ours, theirs)
    assert len(result.items) == 1
    assert result.items[0].name == "Milk"


def test_checked_wins():
    base = _list(Item(name="Milk"))
    ours = _list(Item(name="Milk", checked=False))
    theirs = _list(Item(name="Milk", checked=True))
    result = merge(base, ours, theirs)
    assert result.items[0].checked is True


def test_qty_conflict_ours_wins():
    base = _list(Item(name="Milk"))
    ours = _list(Item(name="Milk", qty=Quantity(2, "l")))
    theirs = _list(Item(name="Milk", qty=Quantity(3, "l")))
    result = merge(base, ours, theirs)
    assert result.items[0].qty == Quantity(2, "l")


def test_qty_present_one_side_kept():
    base = _list(Item(name="Milk"))
    ours = _list(Item(name="Milk", qty=None))
    theirs = _list(Item(name="Milk", qty=Quantity(3, "l")))
    result = merge(base, ours, theirs)
    assert result.items[0].qty == Quantity(3, "l")


def test_deletion_honored_when_surviving_unchanged():
    # In base + ours (unchanged), absent in theirs -> theirs deleted it.
    base = _list(Item(name="Milk"))
    ours = _list(Item(name="Milk"))
    theirs = _list()
    result = merge(base, ours, theirs)
    assert result.items == []


def test_edit_on_surviving_side_beats_deletion():
    # theirs deleted; ours edited (qty) the same-key item -> keep our edit.
    base = _list(Item(name="Milk"))
    ours = _list(Item(name="Milk", qty=Quantity(2, "l")))
    theirs = _list()
    result = merge(base, ours, theirs)
    assert len(result.items) == 1
    assert result.items[0].qty == Quantity(2, "l")


def test_category_change_is_new_identity():
    # Changing category changes the key, so it's an addition on that side and a
    # deletion of the old key; the old (base) key is dropped.
    base = _list(Item(name="Milk", category=None))
    ours = _list(Item(name="Milk", category="Dairy"))
    theirs = _list(Item(name="Milk", category=None))
    result = merge(base, ours, theirs)
    keys = {it.key for it in result.items}
    assert "Dairy|Milk" in keys
    assert "|Milk" not in keys


def test_title_change_one_side_propagates():
    base = _list(title="Rewe")
    ours = _list(title="Rewe")
    theirs = _list(title="Rewe Wochenende")
    result = merge(base, ours, theirs)
    assert result.title == "Rewe Wochenende"


def test_title_tie_prefers_ours():
    base = _list(title="Base")
    ours = _list(title="Ours")
    theirs = _list(title="Theirs")
    result = merge(base, ours, theirs)
    assert result.title == "Ours"


def test_merge_symmetric_for_additions():
    base = _list()
    a = Item(name="Milk")
    b = Item(name="Bread")
    r1 = merge(base, _list(a), _list(b))
    r2 = merge(base, _list(b), _list(a))
    assert {it.name for it in r1.items} == {it.name for it in r2.items} == {
        "Milk",
        "Bread",
    }
