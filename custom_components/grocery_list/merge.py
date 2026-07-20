"""Semantic 3-way merge engine.

Git is only a transport/history layer; ALL merging happens here, on parsed data
models, never on raw text. This keeps the logic VCS-agnostic and more correct
for the domain than a textual merge.

The merge is a classic 3-way merge over three ``GroceryList`` snapshots, keyed
by item identity ``(category, name)``:

- ``base``:   the common ancestor = the git merge-base of ours and theirs.
- ``ours``:   the local working state.
- ``theirs``: the remote state fetched from the git host.

Merge rules (per identity key ``f"{category or ''}|{name}"``):

- Present on both sides -> merge fields (checked = ours or theirs; quantity a
  deterministic winner).
- Present on exactly one side and NOT in base -> an addition; keep it.
- Present in base but missing on a side -> a deletion; honor it (drop).
- ``title``: prefer the side that changed vs base; tie -> ours.

The function is pure and deterministic.
"""

from __future__ import annotations

from .models import GroceryList, Item, identity_key


def key(item: Item) -> str:
    """Return the merge key for an item: ``f"{category or ''}|{name}"``."""
    return identity_key(item.category, item.name)


def _merge_item_fields(ours: Item, theirs: Item) -> Item:
    """Merge two versions of the same item (same identity key).

    ``checked`` uses the 'checked wins' rule. For quantity we pick a
    deterministic winner when the two sides differ: the side that has a
    quantity (preferring ``ours`` when both do). name/category are identical by
    construction (they form the key).
    """
    checked = ours.checked or theirs.checked
    if ours.qty == theirs.qty:
        qty = ours.qty
    elif ours.qty is None:
        qty = theirs.qty
    elif theirs.qty is None:
        qty = ours.qty
    else:
        # Both present and differ -> deterministic last-writer-wins: ours.
        qty = ours.qty
    return Item(
        name=ours.name,
        category=ours.category,
        qty=qty,
        checked=checked,
    )


def merge(
    base: GroceryList, ours: GroceryList, theirs: GroceryList
) -> GroceryList:
    """Perform a semantic 3-way merge of three list snapshots.

    Returns a new ``GroceryList`` with the merged items. Pure and deterministic.
    """
    base_items = {key(it): it for it in base.items}
    our_items = {key(it): it for it in ours.items}
    their_items = {key(it): it for it in theirs.items}

    all_keys = set(base_items) | set(our_items) | set(their_items)

    merged: list[Item] = []
    for k in all_keys:
        in_base = k in base_items
        our_item = our_items.get(k)
        their_item = their_items.get(k)

        if our_item and their_item:
            merged.append(_merge_item_fields(our_item, their_item))
        elif our_item or their_item:
            single = our_item if our_item is not None else their_item
            assert single is not None
            if in_base:
                # Existed in base, gone on one side -> deletion; honor it only
                # if the surviving side is unchanged from base. If the
                # surviving side edited the item, that edit is an addition of a
                # new identity when name/category changed; for same-key edits
                # (qty/checked) we keep the surviving version.
                base_item = base_items[k]
                if single == base_item:
                    # Unchanged on the surviving side -> the other side deleted
                    # it; drop.
                    continue
                merged.append(single)  # edited on surviving side -> keep
            else:
                merged.append(single)  # addition -> keep
        # absent on both -> nothing

    # Title: prefer a side that changed from base; tie -> ours.
    if ours.title != base.title and theirs.title == base.title:
        title = ours.title
    elif theirs.title != base.title and ours.title == base.title:
        title = theirs.title
    else:
        title = ours.title

    return GroceryList(
        slug=ours.slug or theirs.slug or base.slug,
        title=title,
        items=merged,
    )
