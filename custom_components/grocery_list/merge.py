"""Semantic 3-way merge engine (PLAN §2, §3).

This is the heart of conflict resolution. Git is only a transport/history layer;
ALL merging happens here, on parsed data models, never on raw text. This keeps
the logic VCS-agnostic (we could swap dulwich for the git binary without
touching this module) and more correct for the domain than textual merge.

The merge is a classic 3-way merge over three ``ListState`` snapshots:

- ``base``:  the common ancestor = the locally persisted ``last_synced_commit``.
- ``ours``:  the local working state.
- ``theirs``: the remote state fetched from the git host.

Merge rules (per item id):

- Presence/tombstones:
  - If an id is tombstoned on either side, the item is removed in the result,
    UNLESS the other side has a *newer* edit to that item than the deletion
    timestamp (delete-vs-edit resolved by last-writer-wins). The newest
    tombstone timestamp is retained so the deletion propagates.
  - Additions (id present on a side but not in base) are unioned in.
- Field-level for surviving items (name, category, qty): last-writer-wins by
  ``updated_ts`` (string compare works because timestamps are canonical UTC).
- ``checked``: "checked wins" tiebreak — if either side has the item checked,
  the result is checked; ``checked_ts`` takes the earliest non-null check time
  among sides that have it checked (the moment it first became bought).
- ``title``: last-writer-wins is not tracked per-field; we take ``ours`` unless
  it equals base and theirs changed it, in which case we take theirs.

The function is pure and deterministic: given the same three inputs it always
returns the same result, regardless of argument order semantics beyond the
defined ours/theirs roles (and for commutative-safe fields the outcome is the
same if ours/theirs are swapped).
"""

from __future__ import annotations

from .models import Item, ListState, Tombstone


def _max_ts(*values: str | None) -> str:
    """Return the lexicographically greatest (newest) non-empty timestamp."""
    present = [v for v in values if v]
    return max(present) if present else ""


def _merge_checked(ours: Item | None, theirs: Item | None) -> tuple[bool, str | None]:
    """Apply the 'checked wins' rule and compute the resulting checked_ts.

    If either side is checked, the result is checked. The checked_ts is the
    earliest moment any side marked it checked (when it first became bought).
    If neither is checked, result is unchecked with no checked_ts.
    """
    sides = [s for s in (ours, theirs) if s is not None]
    checked = any(s.checked for s in sides)
    if not checked:
        return False, None
    check_times = [
        s.checked_ts for s in sides if s.checked and s.checked_ts
    ]
    return True, (min(check_times) if check_times else None)


def _merge_item_fields(base: Item | None, ours: Item, theirs: Item) -> Item:
    """Merge two versions of the same item using last-writer-wins per field.

    ``base`` is the ancestor version if present (unused for LWW directly but
    kept for clarity/future field-level 3-way refinements). For scalar content
    fields we pick the side with the newer ``updated_ts``; ties favor ``ours``
    for determinism. ``checked`` uses the dedicated 'checked wins' rule.
    """
    winner = ours if ours.updated_ts >= theirs.updated_ts else theirs

    checked, checked_ts = _merge_checked(ours, theirs)

    # created_ts and added_by are immutable facts of first creation; keep the
    # earliest created_ts and the added_by that goes with it.
    if ours.created_ts <= theirs.created_ts:
        created_ts, added_by = ours.created_ts, ours.added_by
    else:
        created_ts, added_by = theirs.created_ts, theirs.added_by

    return Item(
        id=ours.id,
        name=winner.name,
        category=winner.category,
        qty=winner.qty,
        checked=checked,
        added_by=added_by,
        created_ts=created_ts,
        updated_ts=_max_ts(ours.updated_ts, theirs.updated_ts),
        checked_ts=checked_ts,
    )


def _resolve_tombstone(
    item: Item | None,
    our_tomb: Tombstone | None,
    their_tomb: Tombstone | None,
) -> Tombstone | None:
    """Return the surviving tombstone if the item should stay deleted.

    Delete-vs-edit: if the merged/live item has an ``updated_ts`` strictly newer
    than the newest tombstone, the edit wins and the item is resurrected (return
    None). Otherwise the newest tombstone wins.
    """
    tombs = [t for t in (our_tomb, their_tomb) if t is not None]
    if not tombs:
        return None
    newest = max(tombs, key=lambda t: t.deleted_ts)
    if item is not None and item.updated_ts > newest.deleted_ts:
        # A newer edit than the deletion -> resurrect (edit wins).
        return None
    return newest


def merge(base: ListState, ours: ListState, theirs: ListState) -> ListState:
    """Perform a semantic 3-way merge of three list snapshots.

    Returns a new ``ListState`` containing the merged live items and the
    surviving tombstones. Pure and deterministic.
    """
    all_ids = (
        set(base.items)
        | set(ours.items)
        | set(theirs.items)
        | set(base.tombstones)
        | set(ours.tombstones)
        | set(theirs.tombstones)
    )

    merged_items: dict[str, Item] = {}
    merged_tombs: dict[str, Tombstone] = {}

    for iid in all_ids:
        our_item = ours.items.get(iid)
        their_item = theirs.items.get(iid)
        base_item = base.items.get(iid)
        our_tomb = ours.tombstones.get(iid)
        their_tomb = theirs.tombstones.get(iid)

        # First compute the candidate live item (ignoring tombstones).
        if our_item and their_item:
            candidate = _merge_item_fields(base_item, our_item, their_item)
        elif our_item or their_item:
            # Present on exactly one side.
            single = our_item or their_item
            if base_item is None:
                # Addition on one side -> include it.
                candidate = single
            else:
                # Existed in base, deleted on the other side (missing) ->
                # treat missing side as a deletion candidate; keep single for
                # now and let tombstone logic decide. If the other side simply
                # didn't modify, single still represents the latest.
                candidate = single
        else:
            candidate = None

        # Now apply tombstone resolution.
        surviving_tomb = _resolve_tombstone(candidate, our_tomb, their_tomb)

        # Implicit deletion: item existed in base, present on one side only,
        # and absent (not merely unmodified) on the other. We can't distinguish
        # "absent because deleted" from "absent because never fetched" without a
        # tombstone, so we rely on explicit tombstones for deletions. Absent on
        # one side with no tombstone => treated as still-present (union-safe).

        if surviving_tomb is not None:
            merged_tombs[iid] = surviving_tomb
            # Item stays deleted; do not add to merged_items.
            continue

        if candidate is not None:
            merged_items[iid] = candidate

    # Title: last-writer-wins-ish. Prefer a side that changed from base.
    if ours.title != base.title and theirs.title == base.title:
        title = ours.title
    elif theirs.title != base.title and ours.title == base.title:
        title = theirs.title
    else:
        title = ours.title  # tie or both changed -> ours

    return ListState(
        slug=ours.slug or theirs.slug or base.slug,
        title=title,
        items=merged_items,
        tombstones=merged_tombs,
    )
