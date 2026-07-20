"""Unit tests for the data models.

Identity is ``(category, name)``; there are no ids, timestamps, or tombstones.
"""

from grocery_list.models import (
    GroceryList,
    Item,
    Quantity,
    identity_key,
)


def test_identity_key_format():
    assert identity_key("Dairy", "Milk") == "Dairy|Milk"
    assert identity_key(None, "Milk") == "|Milk"
    assert identity_key("", "Milk") == "|Milk"


def test_quantity_roundtrip():
    q = Quantity(value=2.0, unit="pcs")
    assert Quantity.from_dict(q.to_dict()) == q


def test_item_key_property():
    item = Item(name="Milk", category="Dairy")
    assert item.key == "Dairy|Milk"
    assert Item(name="Bread").key == "|Bread"


def test_item_roundtrip():
    item = Item(
        name="Tomatoes",
        category="Vegetables",
        qty=Quantity(2, "pcs"),
        checked=True,
    )
    restored = Item.from_dict(item.to_dict())
    assert restored == item


def test_item_defaults():
    item = Item(name="Bread")
    assert item.category is None
    assert item.qty is None
    assert item.checked is False


def test_item_copy_is_independent():
    item = Item(name="Milk", qty=Quantity(1, "l"))
    clone = item.copy()
    assert clone == item
    clone.checked = True
    clone.qty.value  # noqa: B018 - ensure attribute access works
    assert item.checked is False


def test_grocerylist_item_by_key_and_roundtrip():
    glist = GroceryList(
        slug="rewe",
        title="Rewe",
        items=[
            Item(name="Milk", category="Dairy"),
            Item(name="Bread"),
        ],
    )
    assert glist.item_by_key("Dairy", "Milk").name == "Milk"
    assert glist.item_by_key(None, "Bread").name == "Bread"
    assert glist.item_by_key("Dairy", "Nope") is None
    restored = GroceryList.from_dict(glist.to_dict())
    assert restored == glist
