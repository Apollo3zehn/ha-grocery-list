"""Unit tests for the semantic 3-way merge engine (PLAN §3)."""

from grocery_list.merge import merge
from grocery_list.models import Item, ListState, Tombstone


def _state(*items: Item, tombstones=None, title="Rewe", slug="rewe") -> ListState:
    return ListState(
        slug=slug,
        title=title,
        items={it.id: it for it in items},
        tombstones={t.id: t for t in (tombstones or [])},
    )


def _item(iid, name="X", checked=False, upd="2026-01-01T00:00:00Z", **kw) -> Item:
    return Item(id=iid, name=name, checked=checked, updated_ts=upd, **kw)


def test_disjoint_additions_are_unioned():
    base = _state()
    ours = _state(_item("a", "Milk"))
    theirs = _state(_item("b", "Bread"))
    result = merge(base, ours, theirs)
    assert set(result.items) == {"a", "b"}


def test_same_item_edit_lww_newer_wins():
    base = _state(_item("a", "Milk", upd="2026-01-01T00:00:00Z"))
    ours = _state(_item("a", "Milk 1L", upd="2026-01-02T00:00:00Z"))
    theirs = _state(_item("a", "Milk 2L", upd="2026-01-03T00:00:00Z"))
    result = merge(base, ours, theirs)
    assert result.items["a"].name == "Milk 2L"  # theirs newer
    assert result.items["a"].updated_ts == "2026-01-03T00:00:00Z"


def test_checked_wins_tiebreak():
    base = _state(_item("a", "Milk"))
    ours = _state(_item("a", "Milk", checked=False, upd="2026-01-05T00:00:00Z"))
    theirs = _state(
        _item(
            "a", "Milk", checked=True, upd="2026-01-02T00:00:00Z",
            checked_ts="2026-01-02T00:00:00Z",
        )
    )
    result = merge(base, ours, theirs)
    # Even though ours is newer and unchecked, checked wins.
    assert result.items["a"].checked is True
    assert result.items["a"].checked_ts == "2026-01-02T00:00:00Z"


def test_checked_ts_is_earliest():
    base = _state(_item("a", "Milk"))
    ours = _state(
        _item("a", "Milk", checked=True, checked_ts="2026-01-05T00:00:00Z")
    )
    theirs = _state(
        _item("a", "Milk", checked=True, checked_ts="2026-01-03T00:00:00Z")
    )
    result = merge(base, ours, theirs)
    assert result.items["a"].checked_ts == "2026-01-03T00:00:00Z"


def test_deletion_via_tombstone_removes_item():
    base = _state(_item("a", "Milk"))
    ours = _state(_item("a", "Milk"))
    theirs = _state(
        tombstones=[Tombstone(id="a", deleted_ts="2026-02-01T00:00:00Z")]
    )
    result = merge(base, ours, theirs)
    assert "a" not in result.items
    assert "a" in result.tombstones


def test_delete_vs_newer_edit_resurrects():
    base = _state(_item("a", "Milk", upd="2026-01-01T00:00:00Z"))
    # Our edit is newer than their deletion -> edit wins, item resurrected.
    ours = _state(_item("a", "Milk 2L", upd="2026-03-01T00:00:00Z"))
    theirs = _state(
        tombstones=[Tombstone(id="a", deleted_ts="2026-02-01T00:00:00Z")]
    )
    result = merge(base, ours, theirs)
    assert "a" in result.items
    assert result.items["a"].name == "Milk 2L"
    assert "a" not in result.tombstones


def test_delete_newer_than_edit_stays_deleted():
    base = _state(_item("a", "Milk", upd="2026-01-01T00:00:00Z"))
    ours = _state(_item("a", "Milk 2L", upd="2026-01-15T00:00:00Z"))
    theirs = _state(
        tombstones=[Tombstone(id="a", deleted_ts="2026-02-01T00:00:00Z")]
    )
    result = merge(base, ours, theirs)
    assert "a" not in result.items
    assert "a" in result.tombstones


def test_category_change_lww():
    base = _state(_item("a", "Milk", category=None, upd="2026-01-01T00:00:00Z"))
    ours = _state(
        _item("a", "Milk", category="cat-dairy", upd="2026-01-02T00:00:00Z")
    )
    theirs = _state(
        _item("a", "Milk", category="cat-drinks", upd="2026-01-05T00:00:00Z")
    )
    result = merge(base, ours, theirs)
    assert result.items["a"].category == "cat-drinks"


def test_created_ts_and_added_by_keep_earliest():
    base = _state()
    ours = _state(
        _item(
            "a", "Milk", added_by="pi", created_ts="2026-01-02T00:00:00Z",
            upd="2026-01-02T00:00:00Z",
        )
    )
    theirs = _state(
        _item(
            "a", "Milk", added_by="anna", created_ts="2026-01-01T00:00:00Z",
            upd="2026-01-03T00:00:00Z",
        )
    )
    result = merge(base, ours, theirs)
    # earliest creation wins for created_ts + added_by
    assert result.items["a"].created_ts == "2026-01-01T00:00:00Z"
    assert result.items["a"].added_by == "anna"


def test_title_change_propagates_from_one_side():
    base = _state(title="Rewe")
    ours = _state(title="Rewe")
    theirs = _state(title="Rewe Wochenende")
    result = merge(base, ours, theirs)
    assert result.title == "Rewe Wochenende"


def test_merge_is_deterministic_and_symmetric_for_additions():
    base = _state()
    a = _item("a", "Milk")
    b = _item("b", "Bread")
    r1 = merge(base, _state(a), _state(b))
    r2 = merge(base, _state(b), _state(a))
    assert set(r1.items) == set(r2.items) == {"a", "b"}


def test_newest_tombstone_retained():
    base = _state(_item("a", "Milk"))
    ours = _state(
        tombstones=[Tombstone(id="a", deleted_ts="2026-01-01T00:00:00Z", reason="deleted")]
    )
    theirs = _state(
        tombstones=[Tombstone(id="a", deleted_ts="2026-02-01T00:00:00Z", reason="cleared")]
    )
    result = merge(base, ours, theirs)
    assert result.tombstones["a"].deleted_ts == "2026-02-01T00:00:00Z"
    assert result.tombstones["a"].reason == "cleared"
