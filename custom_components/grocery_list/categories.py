"""User-managed categories (PLAN §4.4).

There are NO developer-shipped categories; the set starts empty and is managed
entirely in the app UI. Category definitions are synced in the repo as JSON at
``.grocery/categories.json`` so every instance shares them.

Like list items, categories merge semantically (never via text): last-writer-
wins by ``updated_ts``, with tombstones for deletions so a delete on one device
doesn't get resurrected by another that still has the category. Deleting a
category does NOT delete its items; the coordinator reassigns affected items to
uncategorized (category=None) — that reassignment is itself an item edit that
merges normally.

Category management actions flow through the shared op-log (PLAN §6) and are
undoable per identity, exactly like item actions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .models import Category, Tombstone, new_id, utcnow_iso


@dataclass(slots=True)
class CategorySet:
    """A mergeable collection of categories plus tombstones.

    Serialized to ``.grocery/categories.json``. The ``categories`` map is keyed
    by category id; ``tombstones`` records deleted category ids with timestamps.
    """

    categories: dict[str, Category] = field(default_factory=dict)
    tombstones: dict[str, Tombstone] = field(default_factory=dict)

    # -- CRUD ---------------------------------------------------------------

    def create(
        self,
        labels: dict[str, str],
        *,
        icon: str | None = None,
        order: int | None = None,
    ) -> Category:
        """Create and insert a new category, returning it.

        ``order`` defaults to the end of the current list.
        """
        if order is None:
            order = self._next_order()
        cat = Category(
            id=new_id("cat-"),
            order=order,
            labels=dict(labels),
            icon=icon,
            updated_ts=utcnow_iso(),
        )
        self.categories[cat.id] = cat
        self.tombstones.pop(cat.id, None)
        return cat

    def update(
        self,
        cat_id: str,
        *,
        labels: dict[str, str] | None = None,
        icon: str | None = None,
        order: int | None = None,
    ) -> Category | None:
        """Update fields of an existing category. Returns the updated category."""
        cat = self.categories.get(cat_id)
        if cat is None:
            return None
        if labels is not None:
            cat.labels = dict(labels)
        if icon is not None:
            cat.icon = icon
        if order is not None:
            cat.order = order
        cat.updated_ts = utcnow_iso()
        return cat

    def delete(self, cat_id: str) -> Tombstone | None:
        """Delete a category, leaving a tombstone. Returns the tombstone."""
        if cat_id not in self.categories:
            return None
        del self.categories[cat_id]
        tomb = Tombstone(id=cat_id, deleted_ts=utcnow_iso(), reason="deleted")
        self.tombstones[cat_id] = tomb
        return tomb

    def reorder(self, ordered_ids: list[str]) -> None:
        """Set category order to match the given id sequence."""
        now = utcnow_iso()
        for index, cat_id in enumerate(ordered_ids):
            cat = self.categories.get(cat_id)
            if cat is not None:
                cat.order = index
                cat.updated_ts = now

    # -- queries ------------------------------------------------------------

    def ordered(self) -> list[Category]:
        """Return live categories sorted by (order, id)."""
        return sorted(
            self.categories.values(), key=lambda c: (c.order, c.id)
        )

    def order_ids(self) -> list[str]:
        return [c.id for c in self.ordered()]

    def labels_map(self, locale: str) -> dict[str, str]:
        return {c.id: c.label(locale) for c in self.categories.values()}

    def _next_order(self) -> int:
        if not self.categories:
            return 0
        return max(c.order for c in self.categories.values()) + 1

    # -- persistence --------------------------------------------------------

    def to_json(self) -> str:
        payload = {
            "categories": [c.to_dict() for c in self.ordered()],
            "tombstones": [t.to_dict() for t in self.tombstones.values()],
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    @classmethod
    def from_json(cls, text: str) -> "CategorySet":
        if not text.strip():
            return cls()
        data = json.loads(text)
        categories = {
            d["id"]: Category.from_dict(d)
            for d in data.get("categories", [])
        }
        tombstones = {
            d["id"]: Tombstone.from_dict(d)
            for d in data.get("tombstones", [])
        }
        return cls(categories=categories, tombstones=tombstones)


def merge_category_sets(
    base: CategorySet, ours: CategorySet, theirs: CategorySet
) -> CategorySet:
    """Semantic 3-way merge of category sets (PLAN §3 applied to categories).

    - Union by id.
    - Both sides present: last-writer-wins by ``updated_ts``.
    - Tombstoned on either side: category removed unless the surviving category
      has a newer ``updated_ts`` than the newest tombstone (edit resurrects).
    - Newest tombstone retained.
    """
    all_ids = (
        set(base.categories)
        | set(ours.categories)
        | set(theirs.categories)
        | set(base.tombstones)
        | set(ours.tombstones)
        | set(theirs.tombstones)
    )

    merged_cats: dict[str, Category] = {}
    merged_tombs: dict[str, Tombstone] = {}

    for cid in all_ids:
        our_cat = ours.categories.get(cid)
        their_cat = theirs.categories.get(cid)

        if our_cat and their_cat:
            candidate = (
                our_cat
                if our_cat.updated_ts >= their_cat.updated_ts
                else their_cat
            )
        else:
            candidate = our_cat or their_cat

        tombs = [
            t
            for t in (ours.tombstones.get(cid), theirs.tombstones.get(cid))
            if t is not None
        ]
        newest_tomb = (
            max(tombs, key=lambda t: t.deleted_ts) if tombs else None
        )

        if newest_tomb is not None:
            if candidate is not None and candidate.updated_ts > newest_tomb.deleted_ts:
                # Edit newer than deletion -> resurrect.
                merged_cats[cid] = candidate
            else:
                merged_tombs[cid] = newest_tomb
            continue

        if candidate is not None:
            merged_cats[cid] = candidate

    return CategorySet(categories=merged_cats, tombstones=merged_tombs)
