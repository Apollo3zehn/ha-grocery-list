"""Unit tests for Markdown serialization/parsing."""

from grocery_list.markdown_io import (
    parse,
    parse_archive,
    serialize,
    serialize_archive,
)
from grocery_list.models import ArchivedItem, GroceryList, Item, Quantity


def _sample_list() -> GroceryList:
    return GroceryList(
        slug="rewe",
        title="Rewe",
        items=[
            Item(
                id="a1b2",
                name="Tomatoes",
                category="cat-veg",
                qty=Quantity(2, "pcs"),
                checked=False,
                added_by="kitchen-pi",
                created_ts="2026-07-19T20:40:00Z",
                updated_ts="2026-07-19T20:40:00Z",
            ),
            Item(
                id="c3d4",
                name="Potatoes",
                category="cat-veg",
                qty=Quantity(1, "kg"),
                checked=True,
                added_by="anna",
                created_ts="2026-07-19T20:30:00Z",
                updated_ts="2026-07-19T20:50:00Z",
                checked_ts="2026-07-19T20:50:00Z",
            ),
            Item(
                id="e5f6",
                name="Milk",
                category="cat-dairy",
                qty=Quantity(2, "l"),
                checked=False,
                added_by="kitchen-pi",
                created_ts="2026-07-19T20:41:00Z",
                updated_ts="2026-07-19T20:41:00Z",
            ),
        ],
    )


def test_serialize_groups_and_sinks_checked():
    glist = _sample_list()
    md = serialize(
        glist,
        category_order=["cat-veg", "cat-dairy"],
        category_labels={"cat-veg": "Vegetables", "cat-dairy": "Dairy"},
    )
    lines = md.splitlines()
    assert lines[0] == "# Rewe"
    # Vegetables section before Dairy
    assert lines.index("## Vegetables") < lines.index("## Dairy")
    # Within Vegetables, unchecked Tomatoes before checked Potatoes
    veg_start = lines.index("## Vegetables")
    tomato_line = next(i for i, l in enumerate(lines) if "Tomatoes" in l)
    potato_line = next(i for i, l in enumerate(lines) if "Potatoes" in l)
    assert veg_start < tomato_line < potato_line
    # Checkbox rendering
    assert any(l.startswith("- [ ] Tomatoes") for l in lines)
    assert any(l.startswith("- [x] Potatoes") for l in lines)


def test_roundtrip_preserves_items():
    glist = _sample_list()
    md = serialize(
        glist,
        category_order=["cat-veg", "cat-dairy"],
        category_labels={"cat-veg": "Vegetables", "cat-dairy": "Dairy"},
    )
    parsed = parse(md)
    # Compare by id-keyed dicts (order differs due to grouping/sinking).
    original = {i.id: i for i in glist.items}
    got = {i.id: i for i in parsed.items}
    assert set(original) == set(got)
    for iid, orig in original.items():
        g = got[iid]
        assert g.name == orig.name
        assert g.category == orig.category
        assert g.qty == orig.qty
        assert g.checked == orig.checked
        assert g.added_by == orig.added_by
        assert g.created_ts == orig.created_ts
        assert g.updated_ts == orig.updated_ts
        assert g.checked_ts == orig.checked_ts


def test_uncategorized_section_rendered_last():
    glist = GroceryList(
        slug="x",
        title="X",
        items=[
            Item(id="u1", name="Mystery", category=None),
            Item(id="v1", name="Carrot", category="cat-veg"),
        ],
    )
    md = serialize(
        glist,
        category_order=["cat-veg"],
        category_labels={"cat-veg": "Vegetables"},
        uncategorized_label="Uncategorized",
    )
    lines = md.splitlines()
    assert lines.index("## Vegetables") < lines.index("## Uncategorized")


def test_parse_fallback_without_metadata():
    md = "# Rewe\n\n## Vegetables\n- [ ] Tomatoes \u00d72 pcs\n- [x] Old Potatoes\n"
    parsed = parse(md)
    names = {i.name: i for i in parsed.items}
    assert "Tomatoes" in names
    assert names["Tomatoes"].qty == Quantity(2, "pcs")
    assert names["Old Potatoes"].checked is True
    # Fallback items get generated ids
    assert all(len(i.id) == 8 for i in parsed.items)


def test_empty_list_serialize_parse():
    glist = GroceryList(slug="empty", title="Empty", items=[])
    md = serialize(glist)
    parsed = parse(md)
    assert parsed.title == "Empty"


def _archived(iid, name, arch_ts, qty=None):
    return ArchivedItem(
        item=Item(
            id=iid,
            name=name,
            category="cat-veg",
            qty=qty,
            checked=True,
            added_by="kitchen-pi",
            created_ts="2026-07-19T20:40:00Z",
            updated_ts="2026-07-19T20:41:00Z",
            checked_ts="2026-07-19T20:41:00Z",
        ),
        archived_ts=arch_ts,
        reason="cleared",
    )


def test_archive_roundtrip_preserves_entries():
    entries = [
        _archived("a1", "Tomatoes", "2026-07-19T21:00:00Z", Quantity(2, "pcs")),
        _archived("a2", "Milk", "2026-07-20T09:00:00Z"),
    ]
    md = serialize_archive("Rewe", entries)
    title, parsed = parse_archive(md)
    assert title == "Rewe"
    by_id = {a.item.id: a for a in parsed}
    assert set(by_id) == {"a1", "a2"}
    assert by_id["a1"].item.qty == Quantity(2, "pcs")
    assert by_id["a1"].archived_ts == "2026-07-19T21:00:00Z"
    assert by_id["a2"].reason == "cleared"
    # All archived items are checked by definition.
    assert all(a.item.checked for a in parsed)


def test_archive_rendered_newest_first():
    entries = [
        _archived("old", "Old", "2026-07-19T21:00:00Z"),
        _archived("new", "New", "2026-07-20T09:00:00Z"),
    ]
    md = serialize_archive("Rewe", entries)
    # The newer entry's line must appear before the older one.
    assert md.index("id:new") < md.index("id:old")


def test_archive_title_suffix_stripped():
    md = serialize_archive("Rewe", [])
    assert md.startswith("# Rewe \u2014 Archive")
    title, parsed = parse_archive(md)
    assert title == "Rewe"
    assert parsed == []


def test_archive_key_is_id_plus_ts():
    a = _archived("a1", "Tomatoes", "2026-07-19T21:00:00Z")
    assert a.key == "a1@2026-07-19T21:00:00Z"
