"""Data models for the Grocery List integration.

These models are the single source of truth. Markdown files are merely a
serialization of these models (see ``markdown_io``), and all conflict
resolution is performed on these structured models (see ``merge``) rather than
on raw text. Keeping the models VCS-agnostic and serialization-agnostic is what
allows git to be a pure transport layer.

Item identity is ``(category, name)`` — there are no persisted ids, timestamps,
or tombstones. Deletions are detected structurally via a git merge-base (see
``merge``), and the archive of cleared items lives in an HA ``Store`` rather
than in git.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace


def identity_key(category: str | None, name: str) -> str:
    """Return the merge/identity key for an item: ``f"{category or ''}|{name}"``.

    Item identity is the ``(category, name)`` pair; this collapses that pair to
    a single stable string used as a dict key by the merge engine and the
    coordinator's mutation lookups.
    """
    return f"{category or ''}|{name}"


# ---------------------------------------------------------------------------
# Quantity
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Quantity:
    """A structured quantity: a numeric value plus a unit id.

    The unit id references an entry in ``units.yaml`` (developer-maintained).
    Quantity is optional on an item; when present, ``value`` is required and
    ``unit`` defaults to ``pcs`` at a higher layer if omitted.
    """

    value: float
    unit: str

    def to_dict(self) -> dict:
        return {"value": self.value, "unit": self.unit}

    @classmethod
    def from_dict(cls, data: dict | None) -> "Quantity | None":
        if not data:
            return None
        return cls(value=float(data["value"]), unit=str(data["unit"]))


# ---------------------------------------------------------------------------
# Item
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Item:
    """A single grocery list item.

    Identity is ``(category, name)``. ``qty`` is optional; ``checked`` uses a
    "checked wins" tiebreak in the merge engine. ``category`` is a user-facing
    category name or ``None`` (uncategorized).
    """

    name: str
    category: str | None = None
    qty: Quantity | None = None
    checked: bool = False

    @property
    def key(self) -> str:
        """The identity key ``f"{category or ''}|{name}"``."""
        return identity_key(self.category, self.name)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "qty": self.qty.to_dict() if self.qty else None,
            "checked": self.checked,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(
            name=str(data["name"]),
            category=data.get("category"),
            qty=Quantity.from_dict(data.get("qty")),
            checked=bool(data.get("checked", False)),
        )

    def copy(self, **changes) -> "Item":
        """Return a shallow copy with the given field changes applied."""
        return replace(self, **changes)


# ---------------------------------------------------------------------------
# GroceryList
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GroceryList:
    """A single grocery list, serialized to ``lists/<slug>.md``.

    ``slug`` is the file stem; ``title`` is the human-facing name rendered as
    the top-level Markdown heading. ``items`` preserves no particular order in
    memory — item display ordering (checked sink to bottom of category) is
    applied by the serializer and the UI.

    ``category_order`` is the user-facing display order of *named* categories.
    It mirrors the order categories appear in the Markdown file (the file is
    authoritative) and is round-tripped by ``markdown_io``. Uncategorized items
    are always rendered last and are not part of this list. Categories present
    in ``items`` but absent from ``category_order`` (e.g. freshly added) are
    appended alphabetically after the known order.
    """

    slug: str
    title: str
    items: list[Item] = field(default_factory=list)
    category_order: list[str] = field(default_factory=list)

    def item_by_key(self, category: str | None, name: str) -> Item | None:
        """Return the item matching ``(category, name)`` or ``None``."""
        target = identity_key(category, name)
        for item in self.items:
            if item.key == target:
                return item
        return None

    def ordered_categories(self) -> list[str]:
        """Return the live named categories in display order.

        Categories that have at least one item, ordered by ``category_order``
        first, then any remaining live categories alphabetically. Uncategorized
        (``None``) is excluded — the UI/serializer render it last on its own.
        """
        live = {it.category for it in self.items if it.category}
        ordered = [c for c in self.category_order if c in live]
        seen = set(ordered)
        ordered.extend(sorted(c for c in live if c not in seen))
        return ordered

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "items": [item.to_dict() for item in self.items],
            "category_order": list(self.category_order),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GroceryList":
        return cls(
            slug=str(data["slug"]),
            title=str(data["title"]),
            items=[Item.from_dict(d) for d in data.get("items", [])],
            category_order=[str(c) for c in data.get("category_order", [])],
        )
