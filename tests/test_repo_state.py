"""Tests for pure repo (de)serialization + whole-repo merge (PLAN §2, §3)."""

from grocery_list.categories import CategorySet
from grocery_list.models import ArchivedItem, Item, ListState, Tombstone
from grocery_list.oplog import OpLog, make_action_op
from grocery_list.repo_state import RepoState, merge_repo_states


def _item(iid, name, cat=None, checked=False, ts="2026-01-01T00:00:00Z"):
    return Item(
        id=iid,
        name=name,
        category=cat,
        checked=checked,
        added_by="pi",
        created_ts=ts,
        updated_ts=ts,
        checked_ts=ts if checked else None,
    )


def test_roundtrip_files_lists_categories_oplog():
    cats = CategorySet()
    veg = cats.create({"en": "Vegetables", "de": "Gem\u00fcse"})
    state = ListState(slug="rewe", title="Rewe")
    state.items = {
        "i1": _item("i1", "Tomatoes", cat=veg.id),
        "i2": _item("i2", "Milk"),
    }
    state.tombstones = {
        "gone": Tombstone(id="gone", deleted_ts="2026-01-02T00:00:00Z")
    }
    oplog = OpLog()
    oplog.append(
        make_action_op(
            identity="pi", entity="item", scope="rewe",
            target_id="i1", before=None, after={"id": "i1"},
        )
    )
    rs = RepoState(lists={"rewe": state}, categories=cats, oplog=oplog)

    files = rs.to_files()
    assert "lists/rewe.md" in files
    assert ".grocery/tombstones/rewe.json" in files
    assert ".grocery/categories.json" in files
    assert ".grocery/oplog.jsonl" in files

    restored = RepoState.from_files(files)
    assert set(restored.lists) == {"rewe"}
    r = restored.lists["rewe"]
    assert r.title == "Rewe"
    assert set(r.items) == {"i1", "i2"}
    assert r.items["i1"].category == veg.id
    assert "gone" in r.tombstones
    assert restored.categories.order_ids() == cats.order_ids()
    assert len(restored.oplog.ops) == 1


def test_from_files_empty():
    rs = RepoState.from_files({})
    assert rs.lists == {}
    assert rs.categories.ordered() == []
    assert rs.oplog.ops == []


def test_from_files_tombstone_without_md_creates_state():
    files = {
        ".grocery/tombstones/ghost.json": (
            b'[{"id": "x", "deleted_ts": "2026-01-01T00:00:00Z", '
            b'"reason": "cleared"}]'
        )
    }
    rs = RepoState.from_files(files)
    assert "ghost" in rs.lists
    assert "x" in rs.lists["ghost"].tombstones


def test_slug_comes_from_filename_not_title():
    files = {"lists/my-store.md": b"# Totally Different Title\n"}
    rs = RepoState.from_files(files)
    assert "my-store" in rs.lists
    assert rs.lists["my-store"].title == "Totally Different Title"


def test_merge_repo_states_union_lists():
    base = RepoState()
    ours = RepoState(
        lists={
            "a": ListState(slug="a", title="A", items={"i1": _item("i1", "X")})
        }
    )
    theirs = RepoState(
        lists={
            "b": ListState(slug="b", title="B", items={"i2": _item("i2", "Y")})
        }
    )
    merged = merge_repo_states(base, ours, theirs)
    assert set(merged.lists) == {"a", "b"}


def test_merge_repo_states_item_addition_within_same_list():
    base = ListState(slug="a", title="A")
    ours = ListState(
        slug="a", title="A", items={"i1": _item("i1", "X")}
    )
    theirs = ListState(
        slug="a", title="A", items={"i2": _item("i2", "Y")}
    )
    merged = merge_repo_states(
        RepoState(lists={"a": base}),
        RepoState(lists={"a": ours}),
        RepoState(lists={"a": theirs}),
    )
    assert set(merged.lists["a"].items) == {"i1", "i2"}


def test_merge_repo_states_oplog_union():
    a = make_action_op(
        identity="pi", entity="item", scope="a",
        target_id="i1", before=None, after={"id": "i1"},
    )
    b = make_action_op(
        identity="tab", entity="item", scope="a",
        target_id="i2", before=None, after={"id": "i2"},
    )
    merged = merge_repo_states(
        RepoState(),
        RepoState(oplog=OpLog([a])),
        RepoState(oplog=OpLog([b])),
    )
    assert {o.op_id for o in merged.oplog.ops} == {a.op_id, b.op_id}


def test_merge_repo_states_checked_wins_across_sides():
    base = ListState(
        slug="a", title="A", items={"i1": _item("i1", "X")}
    )
    ours = ListState(
        slug="a", title="A", items={"i1": _item("i1", "X")}
    )
    theirs_item = _item("i1", "X", checked=True, ts="2026-01-05T00:00:00Z")
    theirs = ListState(slug="a", title="A", items={"i1": theirs_item})
    merged = merge_repo_states(
        RepoState(lists={"a": base}),
        RepoState(lists={"a": ours}),
        RepoState(lists={"a": theirs}),
    )
    assert merged.lists["a"].items["i1"].checked is True


def _archived(iid, name, arch_ts, reason="cleared"):
    return ArchivedItem(
        item=_item(iid, name, checked=True),
        archived_ts=arch_ts,
        reason=reason,
    )


def test_archive_roundtrip_files():
    state = ListState(slug="rewe", title="Rewe")
    rs = RepoState(
        lists={"rewe": state},
        archives={
            "rewe": [
                _archived("a1", "Tomatoes", "2026-07-19T21:00:00Z"),
                _archived("a2", "Milk", "2026-07-20T09:00:00Z"),
            ]
        },
    )
    files = rs.to_files()
    assert "archive/rewe.md" in files

    restored = RepoState.from_files(files)
    entries = restored.archives["rewe"]
    assert {a.item.id for a in entries} == {"a1", "a2"}


def test_archive_empty_not_serialized():
    rs = RepoState(
        lists={"rewe": ListState(slug="rewe", title="Rewe")},
        archives={"rewe": []},
    )
    files = rs.to_files()
    assert "archive/rewe.md" not in files


def test_merge_archives_union_by_key():
    base = RepoState()
    ours = RepoState(
        archives={"a": [_archived("i1", "X", "2026-01-01T00:00:00Z")]}
    )
    theirs = RepoState(
        archives={"a": [_archived("i2", "Y", "2026-01-02T00:00:00Z")]}
    )
    merged = merge_repo_states(base, ours, theirs)
    assert {a.item.id for a in merged.archives["a"]} == {"i1", "i2"}


def test_merge_archives_same_key_deduped():
    e = _archived("i1", "X", "2026-01-01T00:00:00Z")
    ours = RepoState(archives={"a": [e]})
    theirs = RepoState(archives={"a": [e]})
    merged = merge_repo_states(RepoState(), ours, theirs)
    assert len(merged.archives["a"]) == 1


def test_merge_archives_newest_first_sorted():
    older = _archived("i1", "X", "2026-01-01T00:00:00Z")
    newer = _archived("i2", "Y", "2026-01-05T00:00:00Z")
    ours = RepoState(archives={"a": [older]})
    theirs = RepoState(archives={"a": [newer]})
    merged = merge_repo_states(RepoState(), ours, theirs)
    assert [a.item.id for a in merged.archives["a"]] == ["i2", "i1"]


def test_same_id_recleared_appends_distinct_records():
    first = _archived("i1", "X", "2026-01-01T00:00:00Z")
    second = _archived("i1", "X", "2026-01-09T00:00:00Z")
    ours = RepoState(archives={"a": [first]})
    theirs = RepoState(archives={"a": [second]})
    merged = merge_repo_states(RepoState(), ours, theirs)
    assert len(merged.archives["a"]) == 2


# -- list-level tombstones (deleted whole lists) ---------------------------


def test_list_tombstones_roundtrip_files():
    rs = RepoState(
        lists={"gone": ListState(slug="gone", title="Gone")},
        list_tombstones={
            "gone": Tombstone(id="gone", deleted_ts="2026-01-02T00:00:00Z")
        },
    )
    files = rs.to_files()
    # Tombstoned list markdown is NOT written; the sidecar IS.
    assert "lists/gone.md" not in files
    assert ".grocery/list_tombstones.json" in files
    restored = RepoState.from_files(files)
    assert "gone" in restored.list_tombstones


def test_merge_list_tombstone_suppresses_other_side():
    # ours deleted the list; theirs still has it (never fetched the delete).
    ours = RepoState(
        list_tombstones={
            "a": Tombstone(id="a", deleted_ts="2026-02-01T00:00:00Z")
        }
    )
    theirs = RepoState(
        lists={
            "a": ListState(
                slug="a",
                title="A",
                items={"i1": _item("i1", "X", ts="2026-01-01T00:00:00Z")},
            )
        }
    )
    merged = merge_repo_states(RepoState(), ours, theirs)
    assert "a" in merged.list_tombstones
    # Deletion enforced: no live items survive.
    assert not merged.lists["a"].items
    # And the tombstoned list is not serialized back to markdown.
    assert "lists/a.md" not in merged.to_files()


def test_merge_list_tombstone_resurrected_by_newer_edit():
    # theirs re-populated the list AFTER ours deleted it -> list resurrects.
    ours = RepoState(
        list_tombstones={
            "a": Tombstone(id="a", deleted_ts="2026-02-01T00:00:00Z")
        }
    )
    theirs = RepoState(
        lists={
            "a": ListState(
                slug="a",
                title="A",
                items={"i1": _item("i1", "X", ts="2026-03-01T00:00:00Z")},
            )
        }
    )
    merged = merge_repo_states(RepoState(), ours, theirs)
    assert "a" not in merged.list_tombstones
    assert "i1" in merged.lists["a"].items


def test_merge_list_tombstone_newest_wins():
    ours = RepoState(
        list_tombstones={
            "a": Tombstone(id="a", deleted_ts="2026-02-01T00:00:00Z")
        }
    )
    theirs = RepoState(
        list_tombstones={
            "a": Tombstone(id="a", deleted_ts="2026-05-01T00:00:00Z")
        }
    )
    merged = merge_repo_states(RepoState(), ours, theirs)
    assert merged.list_tombstones["a"].deleted_ts == "2026-05-01T00:00:00Z"
