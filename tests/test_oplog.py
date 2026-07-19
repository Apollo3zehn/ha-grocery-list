"""Unit tests for the shared op-log and per-identity undo/redo (PLAN §6)."""

from grocery_list.oplog import (
    ENTITY_ITEM,
    Op,
    OpLog,
    make_action_op,
    merge_oplogs,
)


def _action(identity, target_id, ts, before=None, after=None, label=""):
    op = make_action_op(
        identity=identity,
        entity=ENTITY_ITEM,
        scope="rewe",
        target_id=target_id,
        before=before,
        after=after,
        label=label,
    )
    op.ts = ts  # force deterministic ordering in tests
    return op


def test_action_pushes_undo_clears_redo():
    log = OpLog()
    log.append(_action("pi", "i1", "2026-01-01T00:00:00Z", after={"id": "i1"}))
    assert log.can_undo("pi") is True
    assert log.can_redo("pi") is False
    assert log.peek_undo("pi").target_id == "i1"


def test_per_identity_isolation():
    log = OpLog()
    log.append(_action("pi", "i1", "2026-01-01T00:00:00Z", after={"id": "i1"}))
    log.append(_action("tablet", "i2", "2026-01-01T00:00:01Z", after={"id": "i2"}))
    # pi undoes its own action, not tablet's
    assert log.peek_undo("pi").target_id == "i1"
    assert log.peek_undo("tablet").target_id == "i2"
    assert log.can_undo("other") is False


def test_undo_then_redo_cycle():
    log = OpLog()
    log.append(_action("pi", "i1", "2026-01-01T00:00:00Z", after={"id": "i1"}))

    undo = log.make_undo_marker("pi")
    assert undo is not None and undo.undoes is not None
    undo.ts = "2026-01-01T00:00:02Z"
    log.append(undo)
    assert log.can_undo("pi") is False
    assert log.can_redo("pi") is True

    redo = log.make_redo_marker("pi")
    assert redo is not None and redo.redoes is not None
    redo.ts = "2026-01-01T00:00:03Z"
    log.append(redo)
    assert log.can_undo("pi") is True
    assert log.can_redo("pi") is False


def test_new_action_clears_redo():
    log = OpLog()
    log.append(_action("pi", "i1", "2026-01-01T00:00:00Z", after={"id": "i1"}))
    undo = log.make_undo_marker("pi")
    undo.ts = "2026-01-01T00:00:01Z"
    log.append(undo)
    assert log.can_redo("pi") is True
    # New action should clear redo stack.
    log.append(_action("pi", "i2", "2026-01-01T00:00:02Z", after={"id": "i2"}))
    assert log.can_redo("pi") is False


def test_undo_marker_snapshot_reverts_after_to_before():
    log = OpLog()
    log.append(
        _action(
            "pi", "i1", "2026-01-01T00:00:00Z",
            before=None, after={"id": "i1", "name": "Milk"},
        )
    )
    undo = log.make_undo_marker("pi")
    # Undo of an add => resulting state should delete (after=before=None).
    assert undo.after is None


def test_serialize_parse_roundtrip():
    log = OpLog()
    log.append(_action("pi", "i1", "2026-01-01T00:00:00Z", after={"id": "i1"}))
    log.append(_action("pi", "i2", "2026-01-01T00:00:01Z", after={"id": "i2"}))
    text = log.serialize()
    parsed = OpLog.parse(text)
    assert [o.op_id for o in parsed.ordered()] == [
        o.op_id for o in log.ordered()
    ]


def test_merge_oplogs_union():
    a = _action("pi", "i1", "2026-01-01T00:00:00Z", after={"id": "i1"})
    b = _action("tablet", "i2", "2026-01-01T00:00:01Z", after={"id": "i2"})
    base = OpLog()
    ours = OpLog([a])
    theirs = OpLog([b])
    merged = merge_oplogs(base, ours, theirs)
    ids = {o.op_id for o in merged.ops}
    assert ids == {a.op_id, b.op_id}
    # deterministic order
    assert [o.op_id for o in merged.ordered()] == [a.op_id, b.op_id]


def test_merge_oplogs_dedup_same_op():
    a = _action("pi", "i1", "2026-01-01T00:00:00Z", after={"id": "i1"})
    merged = merge_oplogs(OpLog([a]), OpLog([a]), OpLog([a]))
    assert len(merged.ops) == 1


def test_shared_log_cross_device_undo_consistency():
    # Two identities act; after merging logs, each can independently undo own.
    a = _action("pi", "i1", "2026-01-01T00:00:00Z", after={"id": "i1"})
    b = _action("tablet", "i2", "2026-01-01T00:00:01Z", after={"id": "i2"})
    merged = merge_oplogs(OpLog(), OpLog([a]), OpLog([b]))
    assert merged.peek_undo("pi").target_id == "i1"
    assert merged.peek_undo("tablet").target_id == "i2"
