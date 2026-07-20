"""Shared, synced operation log with per-identity undo/redo (PLAN §6).

The op-log is an append-only JSONL file (``.grocery/oplog.jsonl``) synced through
the git repo. Every user action appends one ``Op``. Undo/redo are **per
identity** (PLAN decision B): an instance can only undo/redo its *own* actions,
even though every instance sees the full shared log.

WHY per-identity and append-only:
- Append-only means the log merges trivially and safely across devices: the
  merge is a union by ``op_id`` (see ``merge_oplogs``). No rewriting history.
- Undo/redo never delete or rewrite ops. Instead they append *marker* ops
  (``undoes``/``redoes`` referencing a prior ``op_id``). The effective undo/redo
  availability is *derived* by deterministically replaying the log. Because the
  replay is a pure function of the (merged) log, every device computes the same
  state.

OP EFFECT MODEL:
Each action op stores a ``before`` and ``after`` snapshot of the affected entity
(item or category). This makes applying undo/redo trivial and robust:
- undo  -> re-apply ``before`` (None means "delete the entity")
- redo  -> re-apply ``after``  (None means "delete the entity")
The coordinator consumes these snapshots to mutate the list/category state, then
appends the corresponding marker op.

REPLAY SEMANTICS (per identity):
- A normal action op pushes its ``op_id`` onto that identity's undo stack and
  clears that identity's redo stack (classic undo/redo behavior).
- An ``undoes=X`` marker pops X from the undo stack and pushes X to the redo
  stack.
- A ``redoes=X`` marker pops X from the redo stack and pushes X to the undo
  stack.
Ops are replayed in a deterministic order: (ts, op_id).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .models import new_id, utcnow_iso

# Entity kinds an op can affect.
ENTITY_ITEM = "item"
ENTITY_CATEGORY = "category"
ENTITY_LIST = "list"


@dataclass(slots=True)
class Op:
    """A single operation in the shared log.

    ``before``/``after`` are serialized entity snapshots (dicts) or ``None``.
    For a plain action exactly one of the following holds:
    - add:    before=None, after=<entity>
    - remove: before=<entity>, after=None
    - update: before=<old>, after=<new>

    ``undoes``/``redoes`` are set ONLY on marker ops and reference the target
    action's ``op_id``. Marker ops also carry the before/after they applied (for
    audit/history), but replay availability is driven by the references.
    """

    op_id: str
    identity: str
    ts: str
    entity: str  # ENTITY_ITEM | ENTITY_CATEGORY
    scope: str  # list slug for items; "" for categories
    target_id: str
    before: dict | None = None
    after: dict | None = None
    undoes: str | None = None
    redoes: str | None = None
    label: str = ""  # optional human-readable action label (e.g. "add_item")
    seq: int = 0  # monotonic per-instance tiebreak for same-``ts`` causal order

    def to_dict(self) -> dict:
        return {
            "op_id": self.op_id,
            "identity": self.identity,
            "ts": self.ts,
            "entity": self.entity,
            "scope": self.scope,
            "target_id": self.target_id,
            "before": self.before,
            "after": self.after,
            "undoes": self.undoes,
            "redoes": self.redoes,
            "label": self.label,
            "seq": self.seq,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Op":
        return cls(
            op_id=str(data["op_id"]),
            identity=str(data.get("identity", "")),
            ts=str(data.get("ts") or utcnow_iso()),
            entity=str(data.get("entity", ENTITY_ITEM)),
            scope=str(data.get("scope", "")),
            target_id=str(data.get("target_id", "")),
            before=data.get("before"),
            after=data.get("after"),
            undoes=data.get("undoes"),
            redoes=data.get("redoes"),
            label=str(data.get("label", "")),
            seq=int(data.get("seq", 0)),
        )

    @property
    def is_marker(self) -> bool:
        return self.undoes is not None or self.redoes is not None


def make_action_op(
    *,
    identity: str,
    entity: str,
    scope: str,
    target_id: str,
    before: dict | None,
    after: dict | None,
    label: str = "",
) -> Op:
    """Create a new normal (non-marker) action op with a fresh id/timestamp."""
    return Op(
        op_id=new_id("op-"),
        identity=identity,
        ts=utcnow_iso(),
        entity=entity,
        scope=scope,
        target_id=target_id,
        before=before,
        after=after,
        label=label,
    )


class OpLog:
    """An in-memory view over the append-only operation log."""

    def __init__(self, ops: list[Op] | None = None) -> None:
        self._ops: list[Op] = list(ops or [])

    # -- persistence --------------------------------------------------------

    @classmethod
    def parse(cls, text: str) -> "OpLog":
        """Parse JSONL text into an OpLog (blank lines ignored)."""
        ops: list[Op] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            ops.append(Op.from_dict(json.loads(line)))
        return cls(ops)

    def serialize(self) -> str:
        """Serialize to JSONL in deterministic (ts, op_id) order."""
        out = []
        for op in self.ordered():
            out.append(json.dumps(op.to_dict(), separators=(",", ":"), sort_keys=True))
        return "\n".join(out) + ("\n" if out else "")

    # -- access -------------------------------------------------------------

    @property
    def ops(self) -> list[Op]:
        return self._ops

    def ordered(self) -> list[Op]:
        """Return ops in deterministic replay order: (ts, seq, op_id).

        ``seq`` is a monotonic per-instance counter that preserves causal order
        among ops sharing the same second-resolution ``ts``. ``op_id`` remains
        the final tiebreak so ops authored on different instances within the
        same second still sort deterministically across all devices.
        """
        return sorted(self._ops, key=lambda o: (o.ts, o.seq, o.op_id))

    def by_id(self, op_id: str) -> Op | None:
        for op in self._ops:
            if op.op_id == op_id:
                return op
        return None

    def append(self, op: Op) -> None:
        """Append an op, assigning a monotonic ``seq`` if it has none.

        The new ``seq`` is one greater than the current maximum so freshly
        appended ops always sort *after* everything already in the log that
        shares their timestamp. Ops that arrive via merge keep their authored
        ``seq`` (they are deduped by ``op_id`` in ``merge_oplogs``).
        """
        if op.seq == 0:
            op.seq = (max((o.seq for o in self._ops), default=0)) + 1
        self._ops.append(op)

    # -- per-identity undo/redo state --------------------------------------

    def _stacks(self) -> dict[str, dict[str, list[str]]]:
        """Compute per-identity undo/redo stacks by replaying the log.

        Returns ``{identity: {"undo": [op_id...], "redo": [op_id...]}}`` where
        the last element of each list is the top of the stack.
        """
        stacks: dict[str, dict[str, list[str]]] = {}

        def ensure(identity: str) -> dict[str, list[str]]:
            return stacks.setdefault(identity, {"undo": [], "redo": []})

        for op in self.ordered():
            st = ensure(op.identity)
            if op.undoes is not None:
                # Move target from undo -> redo stack.
                if op.undoes in st["undo"]:
                    st["undo"].remove(op.undoes)
                st["redo"].append(op.undoes)
            elif op.redoes is not None:
                # Move target from redo -> undo stack.
                if op.redoes in st["redo"]:
                    st["redo"].remove(op.redoes)
                st["undo"].append(op.redoes)
            else:
                # Normal action: push to undo, clear redo (new branch).
                st["undo"].append(op.op_id)
                st["redo"].clear()
        return stacks

    def can_undo(self, identity: str) -> bool:
        st = self._stacks().get(identity)
        return bool(st and st["undo"])

    def can_redo(self, identity: str) -> bool:
        st = self._stacks().get(identity)
        return bool(st and st["redo"])

    def peek_undo(self, identity: str) -> Op | None:
        """Return the action op this identity would undo next (or None)."""
        st = self._stacks().get(identity)
        if not st or not st["undo"]:
            return None
        return self.by_id(st["undo"][-1])

    def peek_redo(self, identity: str) -> Op | None:
        """Return the action op this identity would redo next (or None)."""
        st = self._stacks().get(identity)
        if not st or not st["redo"]:
            return None
        return self.by_id(st["redo"][-1])

    def make_undo_marker(self, identity: str) -> Op | None:
        """Build (but do not append) an undo marker op for this identity.

        Returns None if there is nothing to undo. The caller applies the
        target's ``before`` snapshot to the data model, then appends this op.
        """
        target = self.peek_undo(identity)
        if target is None:
            return None
        return Op(
            op_id=new_id("op-"),
            identity=identity,
            ts=utcnow_iso(),
            entity=target.entity,
            scope=target.scope,
            target_id=target.target_id,
            before=target.after,  # audit: we are reverting after->before
            after=target.before,
            undoes=target.op_id,
            label=f"undo:{target.label}",
        )

    def make_redo_marker(self, identity: str) -> Op | None:
        """Build (but do not append) a redo marker op for this identity.

        Returns None if there is nothing to redo. The caller re-applies the
        target's ``after`` snapshot to the data model, then appends this op.
        """
        target = self.peek_redo(identity)
        if target is None:
            return None
        return Op(
            op_id=new_id("op-"),
            identity=identity,
            ts=utcnow_iso(),
            entity=target.entity,
            scope=target.scope,
            target_id=target.target_id,
            before=target.before,
            after=target.after,
            redoes=target.op_id,
            label=f"redo:{target.label}",
        )


def merge_oplogs(base: OpLog, ours: OpLog, theirs: OpLog) -> OpLog:
    """Merge three op-logs by union of op_ids (append-only => union is correct).

    The base is unused beyond conceptual clarity: since the log is append-only
    and op_ids are globally unique, the merged log is simply the set-union of
    all ops from all three snapshots, kept in deterministic (ts, op_id) order.
    """
    seen: dict[str, Op] = {}
    for log in (base, ours, theirs):
        for op in log.ops:
            seen.setdefault(op.op_id, op)
    merged = OpLog(list(seen.values()))
    # Normalize internal order so serialization is deterministic.
    merged._ops = merged.ordered()  # noqa: SLF001 - internal normalization
    return merged
