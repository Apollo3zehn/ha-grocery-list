"""Tests for pure repo (de)serialization + whole-repo merge.

Only ``lists/<slug>.md`` files are tracked. No tombstones, archives, or
category sidecars live in git; deletions are structural via the merge-base.
"""

from grocery_list.models import GroceryList, Item
from grocery_list.repo_state import RepoState, merge_repo_states


def _list(slug, title, *items: Item) -> GroceryList:
    return GroceryList(slug=slug, title=title, items=list(items))


def test_roundtrip_only_list_files():
    state = _list(
        "rewe",
        "Rewe",
        Item(name="Tomatoes", category="Vegetables"),
        Item(name="Milk"),
    )
    rs = RepoState(lists={"rewe": state})

    # Default (no configured path) stores list files at the repo root.
    files = rs.to_files()
    assert set(files) == {"rewe.md"}
    # No sync metadata files whatsoever.
    assert not any(p.startswith(".grocery/") for p in files)

    restored = RepoState.from_files(files)
    assert set(restored.lists) == {"rewe"}
    r = restored.lists["rewe"]
    assert r.title == "Rewe"
    assert {it.key for it in r.items} == {"Vegetables|Tomatoes", "|Milk"}


def test_roundtrip_with_configured_lists_path():
    state = _list("rewe", "Rewe", Item(name="Milk"))
    rs = RepoState(lists={"rewe": state})

    files = rs.to_files("home/groceries")
    assert set(files) == {"home/groceries/rewe.md"}

    # Wrong/empty prefix must not pick the file up; correct prefix must.
    assert RepoState.from_files(files).lists == {}
    assert RepoState.from_files(files, "home/groceries").lists.keys() == {
        "rewe"
    }


def test_lists_path_normalizes_slashes():
    rs = RepoState(lists={"a": _list("a", "A", Item(name="X"))})
    # Leading/trailing slashes are equivalent to the clean relative form.
    assert set(rs.to_files("/foo/bar/")) == {"foo/bar/a.md"}
    files = {"foo/bar/a.md": b"# A\n"}
    assert RepoState.from_files(files, "foo/bar").lists.keys() == {"a"}


def test_from_files_empty():
    assert RepoState.from_files({}).lists == {}


def test_from_files_ignores_non_list_paths():
    # Default (root) layout: only top-level ``*.md`` files are lists. Nested
    # markdown and non-markdown files are ignored.
    files = {
        "rewe.md": b"# Rewe\n\n- [ ] Milk\n",
        "docs/README.md": b"# not a list\n",
        ".grocery/whatever.json": b"{}",
    }
    rs = RepoState.from_files(files)
    assert set(rs.lists) == {"rewe"}


def test_slug_comes_from_filename_not_title():
    files = {"my-store.md": b"# Totally Different Title\n"}
    rs = RepoState.from_files(files)
    assert "my-store" in rs.lists
    assert rs.lists["my-store"].title == "Totally Different Title"


def test_merge_repo_states_union_lists():
    base = RepoState()
    ours = RepoState(lists={"a": _list("a", "A", Item(name="X"))})
    theirs = RepoState(lists={"b": _list("b", "B", Item(name="Y"))})
    merged = merge_repo_states(base, ours, theirs)
    assert set(merged.lists) == {"a", "b"}


def test_merge_item_addition_within_same_list():
    base = _list("a", "A")
    ours = _list("a", "A", Item(name="X"))
    theirs = _list("a", "A", Item(name="Y"))
    merged = merge_repo_states(
        RepoState(lists={"a": base}),
        RepoState(lists={"a": ours}),
        RepoState(lists={"a": theirs}),
    )
    assert {it.name for it in merged.lists["a"].items} == {"X", "Y"}


def test_merge_checked_wins_across_sides():
    base = _list("a", "A", Item(name="X"))
    ours = _list("a", "A", Item(name="X"))
    theirs = _list("a", "A", Item(name="X", checked=True))
    merged = merge_repo_states(
        RepoState(lists={"a": base}),
        RepoState(lists={"a": ours}),
        RepoState(lists={"a": theirs}),
    )
    assert merged.lists["a"].items[0].checked is True


def test_list_deletion_honored_when_unchanged():
    base = RepoState(lists={"a": _list("a", "A", Item(name="X"))})
    ours = RepoState(lists={"a": _list("a", "A", Item(name="X"))})
    theirs = RepoState()  # theirs deleted the whole list
    merged = merge_repo_states(base, ours, theirs)
    assert "a" not in merged.lists


def test_list_deletion_overridden_by_surviving_edit():
    base = RepoState(lists={"a": _list("a", "A", Item(name="X"))})
    ours = RepoState(lists={"a": _list("a", "A", Item(name="X"),
                                       )})
    # ours added an item; theirs deleted the list -> surviving edit wins.
    ours.lists["a"].items.append(Item(name="Y"))
    theirs = RepoState()
    merged = merge_repo_states(base, ours, theirs)
    assert "a" in merged.lists
    assert {it.name for it in merged.lists["a"].items} == {"X", "Y"}
