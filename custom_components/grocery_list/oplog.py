"""In-memory operation log for per-identity undo/redo.

The op-log is an **in-memory-only** append-only list of :class:`Op` entries. It
is never persisted to disk or synced through git; it exists only for the
lifetime of the running coordinator. Undo/redo are **per identity**: an instance
can only undo/redo its own actions.

WHY append-only + marker ops:
- Undo/redo never delete or rewrite ops. Instead they append *marker* ops
  (``undoes``/``redoes`` referencing a prior ``op_id``). The effective undo/redo
  availability is *derived* by replaying the log.

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
Ops are replayed in insertion order (via a monotonic ``seq``).
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import new_id, utcnow_iso

# Entity kinds an op can affect.
ENTITY_ITEM = "item"
ENTITY_CATEGORY = "category"
ENTITY_LIST = "list"


@dataclass(slots=True)
class Op:
    """A single operation in the in-memory log.

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
    entity: str  # ENTITY_ITEM | ENTITY_CATEGORY | ENTITY_LIST
    scope: str  # list slug for items; "" for categories
    target_id: str
    before: dict | None = None
    after: dict | None = None
    undoes: str | None = None
    redoes: str | None = None
    label: str = ""  # optional human-readable action label (e.g. "add_item")
    seq: int = 0  # monotonic tiebreak preserving insertion (replay) order

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
    """An in-memory append-only operation log with per-identity undo/redo."""

    def __init__(self, ops: list[Op] | None = None) -> None:
        self._ops: list[Op] = list(ops or [])

    # -- access -------------------------------------------------------------

    @property
    def ops(self) -> list[Op]:
        return self._ops

    def ordered(self) -> list[Op]:
        """Return ops in deterministic replay order: (seq, op_id).

        ``seq`` is a monotonic counter assigned on append that preserves the
        insertion (causal) order of operations.
        """
        return sorted(self._ops, key=lambda o: (o.seq, o.op_id))

    def by_id(self, op_id: str) -> Op | None:
        for op in self._ops:
            if op.op_id == op_id:
                return op
        return None

    def append(self, op: Op) -> None:
        """Append an op, assigning a monotonic ``seq`` if it has none.

        The new ``seq`` is one greater than the current maximum so freshly
        appended ops always sort *after* everything already in the log.
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
