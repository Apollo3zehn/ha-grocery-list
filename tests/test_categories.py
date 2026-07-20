"""Unit tests for user-managed categories and their merge (PLAN §4.4, §3)."""

from grocery_list.categories import CategorySet, merge_category_sets
from grocery_list.models import Category, Tombstone


def test_starts_empty():
    cs = CategorySet()
    assert cs.ordered() == []
    assert cs.order_ids() == []


def test_create_assigns_id_and_order():
    cs = CategorySet()
    a = cs.create("Vegetables")
    b = cs.create("Dairy")
    assert a.id.startswith("cat-")
    assert a.order == 0
    assert b.order == 1
    assert cs.order_ids() == [a.id, b.id]


def test_update_changes_fields_and_touches_ts():
    cs = CategorySet()
    a = cs.create("Veg")
    old_ts = a.updated_ts
    a2 = cs.update(a.id, name="Vegetables", icon="mdi:carrot")
    assert a2.name == "Vegetables"
    assert a2.icon == "mdi:carrot"
    assert a2.updated_ts >= old_ts


def test_delete_leaves_tombstone():
    cs = CategorySet()
    a = cs.create("Veg")
    tomb = cs.delete(a.id)
    assert tomb is not None
    assert a.id not in cs.categories
    assert a.id in cs.tombstones


def test_reorder():
    cs = CategorySet()
    a = cs.create("A")
    b = cs.create("B")
    c = cs.create("C")
    cs.reorder([c.id, a.id, b.id])
    assert cs.order_ids() == [c.id, a.id, b.id]


def test_names_map():
    cs = CategorySet()
    a = cs.create("Vegetables")
    names = cs.names_map()
    assert names[a.id] == "Vegetables"


def test_json_roundtrip():
    cs = CategorySet()
    cs.create("Vegetables", icon="mdi:carrot")
    cs.create("Dairy")
    text = cs.to_json()
    restored = CategorySet.from_json(text)
    assert restored.order_ids() == cs.order_ids()
    assert restored.names_map() == cs.names_map()


def test_from_json_empty():
    assert CategorySet.from_json("").ordered() == []
    assert CategorySet.from_json("   ").ordered() == []


def test_merge_union_of_new_categories():
    base = CategorySet()
    ours = CategorySet()
    a = ours.create("Veg")
    theirs = CategorySet()
    b = theirs.create("Dairy")
    merged = merge_category_sets(base, ours, theirs)
    assert set(merged.categories) == {a.id, b.id}


def test_merge_lww_on_conflicting_edit():
    shared = Category(id="cat-x", order=0, name="Old", updated_ts="2026-01-01T00:00:00Z")
    base = CategorySet(categories={"cat-x": shared})
    ours = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", order=0, name="Ours", updated_ts="2026-01-02T00:00:00Z")
        }
    )
    theirs = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", order=0, name="Theirs", updated_ts="2026-01-03T00:00:00Z")
        }
    )
    merged = merge_category_sets(base, ours, theirs)
    assert merged.categories["cat-x"].name == "Theirs"


def test_merge_delete_wins_when_newer():
    base = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", name="X", updated_ts="2026-01-01T00:00:00Z")
        }
    )
    ours = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", name="X", updated_ts="2026-01-01T00:00:00Z")
        }
    )
    theirs = CategorySet(
        tombstones={"cat-x": Tombstone(id="cat-x", deleted_ts="2026-02-01T00:00:00Z")}
    )
    merged = merge_category_sets(base, ours, theirs)
    assert "cat-x" not in merged.categories
    assert "cat-x" in merged.tombstones


def test_merge_edit_resurrects_over_older_delete():
    base = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", name="X", updated_ts="2026-01-01T00:00:00Z")
        }
    )
    ours = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", name="X2", updated_ts="2026-03-01T00:00:00Z")
        }
    )
    theirs = CategorySet(
        tombstones={"cat-x": Tombstone(id="cat-x", deleted_ts="2026-02-01T00:00:00Z")}
    )
    merged = merge_category_sets(base, ours, theirs)
    assert "cat-x" in merged.categories
    assert merged.categories["cat-x"].name == "X2"
