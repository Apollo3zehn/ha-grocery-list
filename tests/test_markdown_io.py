"""Unit tests for Markdown serialization/parsing.

The on-disk format is clean and metadata-free: item identity is
``(category, name)`` and only name/category/qty/checked are persisted.
"""

from grocery_list.markdown_io import parse, serialize
from grocery_list.models import GroceryList, Item, Quantity


def _sample_list() -> GroceryList:
    return GroceryList(
        slug="rewe",
        title="Rewe",
        items=[
            Item(name="Tomatoes", category="Vegetables", qty=Quantity(2, "pcs")),
            Item(name="Potatoes", category="Vegetables", qty=Quantity(1, "kg"),
                 checked=True),
            Item(name="Milk", category="Dairy", qty=Quantity(2, "l")),
        ],
    )


def test_serialize_groups_and_sinks_checked():
    glist = _sample_list()
    md = serialize(glist)
    lines = md.splitlines()
    assert lines[0] == "# Rewe"
    # Categories alphabetical: Dairy before Vegetables.
    assert lines.index("## Dairy") < lines.index("## Vegetables")
    # Within Vegetables, unchecked Tomatoes before checked Potatoes.
    veg_start = lines.index("## Vegetables")
    tomato_line = next(i for i, l in enumerate(lines) if "Tomatoes" in l)
    potato_line = next(i for i, l in enumerate(lines) if "Potatoes" in l)
    assert veg_start < tomato_line < potato_line
    assert any(l.startswith("- [ ] Tomatoes") for l in lines)
    assert any(l.startswith("- [x] Potatoes") for l in lines)


def test_no_hidden_metadata():
    md = serialize(_sample_list())
    assert "<!--" not in md
    assert "id:" not in md
    assert "_ts" not in md


def test_roundtrip_preserves_items():
    glist = _sample_list()
    parsed = parse(serialize(glist))
    original = {it.key: it for it in glist.items}
    got = {it.key: it for it in parsed.items}
    assert set(original) == set(got)
    for k, orig in original.items():
        g = got[k]
        assert g.name == orig.name
        assert g.category == orig.category
        assert g.qty == orig.qty
        assert g.checked == orig.checked


def test_uncategorized_section_rendered_last():
    glist = GroceryList(
        slug="x",
        title="X",
        items=[
            Item(name="Mystery", category=None),
            Item(name="Carrot", category="Vegetables"),
        ],
    )
    md = serialize(glist, uncategorized_label="Uncategorized")
    lines = md.splitlines()
    assert lines.index("## Vegetables") < lines.index("## Uncategorized")


def test_uncategorized_label_roundtrips_to_none():
    glist = GroceryList(slug="x", title="X",
                        items=[Item(name="Salt", category=None)])
    md = serialize(glist, uncategorized_label="Uncategorized")
    parsed = parse(md, uncategorized_label="Uncategorized")
    assert parsed.items[0].category is None


def test_category_name_with_spaces_roundtrips():
    glist = GroceryList(
        slug="x",
        title="X",
        items=[Item(name="Cream", category="Dairy & Eggs")],
    )
    md = serialize(glist)
    assert "## Dairy & Eggs" in md
    parsed = parse(md)
    assert parsed.items[0].category == "Dairy & Eggs"


def test_parse_qty_and_checkbox():
    md = "# Rewe\n\n## Vegetables\n- [ ] Tomatoes \u00d72 pcs\n- [x] Old Potatoes\n"
    parsed = parse(md)
    names = {i.name: i for i in parsed.items}
    assert names["Tomatoes"].qty == Quantity(2, "pcs")
    assert names["Old Potatoes"].checked is True
    assert names["Tomatoes"].category == "Vegetables"


def test_empty_list_serialize_parse():
    glist = GroceryList(slug="empty", title="Empty", items=[])
    parsed = parse(serialize(glist))
    assert parsed.title == "Empty"
    assert parsed.items == []
