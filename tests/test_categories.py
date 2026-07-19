"""Unit tests for user-managed categories and their merge (PLAN §4.4, §3)."""

from grocery_list.categories import CategorySet, merge_category_sets
from grocery_list.models import Category, Tombstone


def test_starts_empty():
    cs = CategorySet()
    assert cs.ordered() == []
    assert cs.order_ids() == []


def test_create_assigns_id_and_order():
    cs = CategorySet()
    a = cs.create({"en": "Vegetables", "de": "Gem\u00fcse"})
    b = cs.create({"en": "Dairy"})
    assert a.id.startswith("cat-")
    assert a.order == 0
    assert b.order == 1
    assert cs.order_ids() == [a.id, b.id]


def test_update_changes_fields_and_touches_ts():
    cs = CategorySet()
    a = cs.create({"en": "Veg"})
    old_ts = a.updated_ts
    a2 = cs.update(a.id, labels={"en": "Vegetables"}, icon="mdi:carrot")
    assert a2.labels["en"] == "Vegetables"
    assert a2.icon == "mdi:carrot"
    assert a2.updated_ts >= old_ts


def test_delete_leaves_tombstone():
    cs = CategorySet()
    a = cs.create({"en": "Veg"})
    tomb = cs.delete(a.id)
    assert tomb is not None
    assert a.id not in cs.categories
    assert a.id in cs.tombstones


def test_reorder():
    cs = CategorySet()
    a = cs.create({"en": "A"})
    b = cs.create({"en": "B"})
    c = cs.create({"en": "C"})
    cs.reorder([c.id, a.id, b.id])
    assert cs.order_ids() == [c.id, a.id, b.id]


def test_labels_map_locale_fallback():
    cs = CategorySet()
    a = cs.create({"en": "Vegetables"})  # no de
    labels = cs.labels_map("de")
    assert labels[a.id] == "Vegetables"  # falls back to en


def test_json_roundtrip():
    cs = CategorySet()
    cs.create({"en": "Vegetables", "de": "Gem\u00fcse"}, icon="mdi:carrot")
    cs.create({"en": "Dairy"})
    text = cs.to_json()
    restored = CategorySet.from_json(text)
    assert restored.order_ids() == cs.order_ids()
    assert restored.labels_map("en") == cs.labels_map("en")


def test_from_json_empty():
    assert CategorySet.from_json("").ordered() == []
    assert CategorySet.from_json("   ").ordered() == []


def test_merge_union_of_new_categories():
    base = CategorySet()
    ours = CategorySet()
    a = ours.create({"en": "Veg"})
    theirs = CategorySet()
    b = theirs.create({"en": "Dairy"})
    merged = merge_category_sets(base, ours, theirs)
    assert set(merged.categories) == {a.id, b.id}


def test_merge_lww_on_conflicting_edit():
    shared = Category(id="cat-x", order=0, labels={"en": "Old"}, updated_ts="2026-01-01T00:00:00Z")
    base = CategorySet(categories={"cat-x": shared})
    ours = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", order=0, labels={"en": "Ours"}, updated_ts="2026-01-02T00:00:00Z")
        }
    )
    theirs = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", order=0, labels={"en": "Theirs"}, updated_ts="2026-01-03T00:00:00Z")
        }
    )
    merged = merge_category_sets(base, ours, theirs)
    assert merged.categories["cat-x"].labels["en"] == "Theirs"


def test_merge_delete_wins_when_newer():
    base = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", labels={"en": "X"}, updated_ts="2026-01-01T00:00:00Z")
        }
    )
    ours = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", labels={"en": "X"}, updated_ts="2026-01-01T00:00:00Z")
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
            "cat-x": Category(id="cat-x", labels={"en": "X"}, updated_ts="2026-01-01T00:00:00Z")
        }
    )
    ours = CategorySet(
        categories={
            "cat-x": Category(id="cat-x", labels={"en": "X2"}, updated_ts="2026-03-01T00:00:00Z")
        }
    )
    theirs = CategorySet(
        tombstones={"cat-x": Tombstone(id="cat-x", deleted_ts="2026-02-01T00:00:00Z")}
    )
    merged = merge_category_sets(base, ours, theirs)
    assert "cat-x" in merged.categories
    assert merged.categories["cat-x"].labels["en"] == "X2"
