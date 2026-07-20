"""Data models for the Grocery List integration.

These models are the single source of truth. Markdown files are merely a
serialization of these models (see ``markdown_io``), and all conflict
resolution is performed on these structured models (see ``merge``) rather than
on raw text. Keeping the models VCS-agnostic and serialization-agnostic is what
allows git to be a pure transport layer (see PLAN §2).

All models are plain dataclasses with explicit ``to_dict``/``from_dict`` helpers
so they can be embedded in Markdown metadata, JSON (categories), or JSONL
(op-log) without pulling in Home Assistant or any VCS dependency.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def utcnow_iso() -> str:
    """Return the current UTC time as an ISO-8601 string with 'Z' suffix.

    A single canonical timestamp format is used everywhere so that string
    comparison of timestamps is equivalent to chronological comparison, which
    the merge engine relies on for last-writer-wins.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_id(prefix: str = "") -> str:
    """Generate a short, stable, collision-resistant id.

    Ids are the basis for all semantic merging, so they must be unique across
    devices without coordination. A random token is sufficient.
    """
    token = secrets.token_hex(4)
    return f"{prefix}{token}" if prefix else token


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

    Fields map directly to PLAN §4.1. ``updated_ts`` drives last-writer-wins in
    the merge engine; ``checked`` uses a "checked wins" tiebreak. ``category``
    references a user-managed category id or is ``None`` (uncategorized).
    """

    id: str
    name: str
    category: str | None = None
    qty: Quantity | None = None
    checked: bool = False
    added_by: str = ""
    created_ts: str = field(default_factory=utcnow_iso)
    updated_ts: str = field(default_factory=utcnow_iso)
    checked_ts: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "qty": self.qty.to_dict() if self.qty else None,
            "checked": self.checked,
            "added_by": self.added_by,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
            "checked_ts": self.checked_ts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            category=data.get("category"),
            qty=Quantity.from_dict(data.get("qty")),
            checked=bool(data.get("checked", False)),
            added_by=str(data.get("added_by", "")),
            created_ts=str(data.get("created_ts") or utcnow_iso()),
            updated_ts=str(data.get("updated_ts") or utcnow_iso()),
            checked_ts=data.get("checked_ts"),
        )

    def copy(self, **changes) -> "Item":
        """Return a shallow copy with the given field changes applied."""
        return replace(self, **changes)


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Category:
    """A user-managed category (PLAN §4.4).

    There are no developer-shipped categories; the set starts empty and is
    managed entirely through the app UI, synced via the repo. Categories are
    language-independent: ``name`` is a single free-text display name.
    """

    id: str
    order: int = 0
    name: str = ""
    icon: str | None = None
    updated_ts: str = field(default_factory=utcnow_iso)

    def display(self) -> str:
        """Return the display name, falling back to the id when empty."""
        return self.name or self.id

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order": self.order,
            "name": self.name,
            "icon": self.icon,
            "updated_ts": self.updated_ts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        return cls(
            id=str(data["id"]),
            order=int(data.get("order", 0)),
            name=str(data.get("name") or ""),
            icon=data.get("icon"),
            updated_ts=str(data.get("updated_ts") or utcnow_iso()),
        )


# ---------------------------------------------------------------------------
# GroceryList
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Tombstone:
    """A record that an item (or category) was removed (PLAN §3, §4.6).

    Tombstones carry a timestamp so the merge engine can resolve delete-vs-edit
    conflicts by last-writer-wins, and a ``reason`` so the UI/archive flow can
    distinguish a plain delete from a "clear checked" archival or an auto-purge.
    Tombstones are stored outside the human-readable list files (in the synced
    ``.grocery`` metadata / derived from the op-log) to keep list files clean.
    """

    id: str
    deleted_ts: str = field(default_factory=utcnow_iso)
    reason: str = "deleted"  # deleted | cleared | archived | purged

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "deleted_ts": self.deleted_ts,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tombstone":
        return cls(
            id=str(data["id"]),
            deleted_ts=str(data.get("deleted_ts") or utcnow_iso()),
            reason=str(data.get("reason", "deleted")),
        )


@dataclass(slots=True)
class ArchivedItem:
    """An item that was cleared out of a live list into the archive (PLAN §4.6).

    Wraps the original :class:`Item` snapshot (preserving id, name, qty, etc.)
    plus ``archived_ts`` — the moment it left the live list. ``reason`` mirrors
    the tombstone reason (``cleared`` for the clear-checked flow). Archived
    items are append-only and browsable in a subview; auto-purge removes those
    older than the configured retention window.

    The archive is keyed by ``(id, archived_ts)`` so re-archiving an id later
    (after it was re-added and cleared again) appends a new record rather than
    clobbering the prior one.
    """

    item: "Item"
    archived_ts: str = field(default_factory=utcnow_iso)
    reason: str = "cleared"

    @property
    def key(self) -> str:
        """Stable de-dupe key for append-only merge (id + archived_ts)."""
        return f"{self.item.id}@{self.archived_ts}"

    def to_dict(self) -> dict:
        return {
            "item": self.item.to_dict(),
            "archived_ts": self.archived_ts,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArchivedItem":
        return cls(
            item=Item.from_dict(data["item"]),
            archived_ts=str(data.get("archived_ts") or utcnow_iso()),
            reason=str(data.get("reason", "cleared")),
        )


@dataclass(slots=True)
class GroceryList:
    """A single grocery list, serialized to ``lists/<slug>.md``.

    ``slug`` is the file stem; ``title`` is the human-facing name rendered as
    the top-level Markdown heading. ``items`` preserves no particular order in
    memory — display ordering (group by category, checked sink to bottom of
    category) is applied by the serializer and the UI.
    """

    slug: str
    title: str
    items: list[Item] = field(default_factory=list)

    def item_by_id(self, item_id: str) -> Item | None:
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GroceryList":
        return cls(
            slug=str(data["slug"]),
            title=str(data["title"]),
            items=[Item.from_dict(d) for d in data.get("items", [])],
        )


@dataclass(slots=True)
class ListState:
    """The full mergeable state of one list: its items plus tombstones.

    The merge engine (see ``merge``) operates on ``ListState`` rather than on
    ``GroceryList`` alone, because correct 3-way merging requires knowing which
    ids were intentionally removed (tombstones) versus never seen. The list
    files on disk store only live items; tombstones live in synced ``.grocery``
    metadata and are recombined into a ``ListState`` for merging.
    """

    slug: str
    title: str
    items: dict[str, Item] = field(default_factory=dict)
    tombstones: dict[str, Tombstone] = field(default_factory=dict)

    @classmethod
    def from_list(
        cls, glist: GroceryList, tombstones: list[Tombstone] | None = None
    ) -> "ListState":
        return cls(
            slug=glist.slug,
            title=glist.title,
            items={it.id: it for it in glist.items},
            tombstones={t.id: t for t in (tombstones or [])},
        )

    def to_list(self) -> GroceryList:
        """Project back to a GroceryList (live items only)."""
        return GroceryList(
            slug=self.slug,
            title=self.title,
            items=list(self.items.values()),
        )

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "items": [it.to_dict() for it in self.items.values()],
            "tombstones": [t.to_dict() for t in self.tombstones.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ListState":
        return cls(
            slug=str(data["slug"]),
            title=str(data["title"]),
            items={
                d["id"]: Item.from_dict(d) for d in data.get("items", [])
            },
            tombstones={
                d["id"]: Tombstone.from_dict(d)
                for d in data.get("tombstones", [])
            },
        )
