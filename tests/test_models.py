"""Unit tests for the data models."""

from grocery_list.models import (
    Category,
    GroceryList,
    Item,
    Quantity,
    new_id,
    utcnow_iso,
)


def test_new_id_unique_and_prefixed():
    a = new_id()
    b = new_id()
    assert a != b
    assert len(a) == 8
    assert new_id("cat-").startswith("cat-")


def test_utcnow_iso_format():
    ts = utcnow_iso()
    # e.g. 2026-07-19T20:40:00Z
    assert ts.endswith("Z")
    assert "T" in ts
    assert len(ts) == 20


def test_quantity_roundtrip():
    q = Quantity(value=2.0, unit="pcs")
    assert Quantity.from_dict(q.to_dict()) == q
    assert Quantity.from_dict(None) is None


def test_item_roundtrip():
    item = Item(
        id="a1b2",
        name="Tomatoes",
        category="cat-veg",
        qty=Quantity(2, "pcs"),
        checked=False,
        added_by="kitchen-pi",
    )
    restored = Item.from_dict(item.to_dict())
    assert restored == item


def test_item_copy():
    item = Item(id="x", name="Milk")
    checked = item.copy(checked=True)
    assert checked.checked is True
    assert item.checked is False
    assert checked.id == item.id


def test_category_label_fallback():
    cat = Category(id="cat-veg", labels={"en": "Vegetables"})
    assert cat.label("en") == "Vegetables"
    # de missing -> falls back to en
    assert cat.label("de") == "Vegetables"
    # both missing -> falls back to id
    empty = Category(id="cat-x")
    assert empty.label("de") == "cat-x"


def test_category_roundtrip():
    cat = Category(
        id="cat-veg",
        order=1,
        labels={"en": "Vegetables", "de": "Gem\u00fcse"},
        icon="mdi:carrot",
    )
    assert Category.from_dict(cat.to_dict()) == cat


def test_grocerylist_item_by_id_and_roundtrip():
    glist = GroceryList(
        slug="rewe",
        title="Rewe",
        items=[Item(id="i1", name="Milk"), Item(id="i2", name="Bread")],
    )
    assert glist.item_by_id("i2").name == "Bread"
    assert glist.item_by_id("nope") is None
    restored = GroceryList.from_dict(glist.to_dict())
    assert restored == glist
