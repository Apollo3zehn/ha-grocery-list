"""Markdown serialization/parsing for grocery lists (PLAN §4.2).

A list file (``lists/<slug>.md``) is a human-readable rendering plus hidden
HTML-comment metadata that makes each item machine-parseable and merge-ready.
The Markdown is a *projection* of the model: the model is authoritative, and
this module must round-trip losslessly (parse(serialize(x)) == x for the
fields that are persisted).

Layout rules:
- ``# <title>`` is the top-level heading.
- Each category is a ``## <name>`` section. Items are ``- [ ]``/``- [x]``.
- The set of categories is derived from the items' ``category`` name field;
  sections are ordered alphabetically by name. Within a category, unchecked
  items come first and checked items sink to the bottom (PLAN §1, §4.2).
- Items whose ``category`` is ``None`` are rendered last under an
  "Uncategorized" section, whose label is provided by the caller (localized).
- Metadata is stored in a trailing HTML comment per item:
  ``<!-- id:.. cat:.. by:.. qty:VALUE:UNIT ts:.. upd:.. checked_ts:.. -->``
  The ``cat`` value is percent-encoded since a category name may contain
  spaces (which would otherwise break the whitespace-delimited comment body).

The parser is tolerant: it reconstructs items purely from the metadata comment
when present (the visible text is for humans and the git host). If an item line
has no metadata comment (e.g. a user hand-edited the file on the host), the
parser falls back to deriving a new item from the visible text so nothing is
lost.
"""

from __future__ import annotations

import re
from urllib.parse import quote, unquote

from .models import (
    ArchivedItem,
    GroceryList,
    Item,
    Quantity,
    new_id,
    utcnow_iso,
)

# ---------------------------------------------------------------------------
# Metadata comment encoding
# ---------------------------------------------------------------------------

_META_RE = re.compile(r"<!--\s*(?P<body>.*?)\s*-->\s*$")
_ITEM_RE = re.compile(r"^\s*-\s*\[(?P<check>[ xX])\]\s*(?P<rest>.*?)\s*$")
_H1_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$")
_H2_RE = re.compile(r"^##\s+(?P<label>.+?)\s*$")


def _encode_meta(item: Item) -> str:
    """Encode item metadata into a compact, order-stable comment body."""
    parts = [f"id:{item.id}"]
    parts.append(
        f"cat:{quote(item.category, safe='')}" if item.category else "cat:-"
    )
    parts.append(f"by:{item.added_by}" if item.added_by else "by:-")
    if item.qty is not None:
        # value:unit; render integers without trailing .0 for readability
        value = item.qty.value
        value_str = str(int(value)) if float(value).is_integer() else str(value)
        parts.append(f"qty:{value_str}:{item.qty.unit}")
    parts.append(f"ts:{item.created_ts}")
    parts.append(f"upd:{item.updated_ts}")
    if item.checked_ts:
        parts.append(f"checked_ts:{item.checked_ts}")
    return " ".join(parts)


def _parse_meta(body: str) -> dict:
    """Parse a metadata comment body into a dict of raw string fields."""
    out: dict[str, str] = {}
    for token in body.split():
        if ":" not in token:
            continue
        key, _, value = token.partition(":")
        # qty has the form qty:VALUE:UNIT -> value is 'VALUE:UNIT'
        out[key] = value
    return out


def _qty_from_meta(raw: str | None) -> Quantity | None:
    if not raw:
        return None
    # raw is 'VALUE:UNIT'
    value_str, _, unit = raw.partition(":")
    if not unit:
        return None
    try:
        return Quantity(value=float(value_str), unit=unit)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Human-readable item text
# ---------------------------------------------------------------------------


def _render_item_text(item: Item) -> str:
    """Render the visible portion of an item line (without checkbox/meta)."""
    text = item.name
    if item.qty is not None:
        value = item.qty.value
        value_str = str(int(value)) if float(value).is_integer() else str(value)
        text = f"{text} \u00d7{value_str} {item.qty.unit}"
    return text


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def serialize(
    glist: GroceryList,
    *,
    uncategorized_label: str = "Uncategorized",
) -> str:
    """Serialize a GroceryList to Markdown text.

    The set of category sections is derived from the items' ``category`` name
    field and ordered alphabetically. Items with a ``None`` category are
    grouped under ``uncategorized_label`` last. The ``## <name>`` heading is
    the category name itself.
    """
    # Bucket items by category name (None -> sentinel key "").
    buckets: dict[str, list[Item]] = {}
    for item in glist.items:
        key = item.category if item.category else ""
        buckets.setdefault(key, []).append(item)

    # Section order: category names alphabetically, then uncategorized last.
    ordered_keys: list[str] = sorted(k for k in buckets if k)
    if "" in buckets:
        ordered_keys.append("")

    lines: list[str] = [f"# {glist.title}", ""]
    for key in ordered_keys:
        items = buckets[key]
        # Sink checked items to the bottom of the category; keep a stable order
        # otherwise (by created_ts then name for determinism).
        items_sorted = sorted(
            items,
            key=lambda it: (it.checked, it.created_ts, it.name.lower()),
        )
        label = key if key else uncategorized_label
        lines.append(f"## {label}")
        for item in items_sorted:
            box = "x" if item.checked else " "
            text = _render_item_text(item)
            meta = _encode_meta(item)
            lines.append(f"- [{box}] {text} <!-- {meta} -->")
        lines.append("")

    # Ensure trailing newline, single.
    return "\n".join(lines).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _strip_meta_from_rest(rest: str) -> tuple[str, dict | None]:
    """Split an item line remainder into (visible_text, meta_dict|None)."""
    match = _META_RE.search(rest)
    if not match:
        return rest.strip(), None
    body = match.group("body")
    visible = rest[: match.start()].strip()
    return visible, _parse_meta(body)


def _visible_to_name_qty(visible: str) -> tuple[str, Quantity | None]:
    """Best-effort parse of 'Name ×VALUE UNIT' visible text (fallback path)."""
    # Match a trailing ' ×<value> <unit>' pattern.
    m = re.search(r"\s\u00d7\s*(\d+(?:\.\d+)?)\s+(\S+)\s*$", visible)
    if not m:
        return visible.strip(), None
    name = visible[: m.start()].strip()
    try:
        qty = Quantity(value=float(m.group(1)), unit=m.group(2))
    except ValueError:
        return visible.strip(), None
    return name, qty


def parse(text: str) -> GroceryList:
    """Parse Markdown text into a GroceryList.

    The slug is not encoded in the file; callers set it from the filename. Here
    we default slug to a slugified title, which callers typically override.
    """
    title = ""
    current_category: str | None = None
    items: list[Item] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")

        h1 = _H1_RE.match(line)
        if h1 and not title:
            title = h1.group("title").strip()
            continue

        h2 = _H2_RE.match(line)
        if h2:
            # Section header. We cannot map a localized label back to a
            # category id reliably, so category identity comes from item
            # metadata; the header only scopes fallback items. We record the
            # raw header label but rely on per-item cat metadata primarily.
            current_category = None  # reset; per-item meta is authoritative
            continue

        item_match = _ITEM_RE.match(line)
        if not item_match:
            continue

        checked = item_match.group("check").lower() == "x"
        visible, meta = _strip_meta_from_rest(item_match.group("rest"))

        if meta and "id" in meta:
            category = meta.get("cat")
            if category in (None, "-", ""):
                category = None
            else:
                category = unquote(category)
            added_by = meta.get("by")
            if added_by in (None, "-"):
                added_by = ""
            item = Item(
                id=meta["id"],
                name=_visible_to_name_qty(visible)[0] or visible,
                category=category,
                qty=_qty_from_meta(meta.get("qty")),
                checked=checked,
                added_by=added_by or "",
                created_ts=meta.get("ts") or utcnow_iso(),
                updated_ts=meta.get("upd") or meta.get("ts") or utcnow_iso(),
                checked_ts=meta.get("checked_ts"),
            )
        else:
            # Fallback: no metadata (hand-edited on host). Derive a fresh item.
            name, qty = _visible_to_name_qty(visible)
            now = utcnow_iso()
            item = Item(
                id=new_id(),
                name=name,
                category=current_category,
                qty=qty,
                checked=checked,
                added_by="",
                created_ts=now,
                updated_ts=now,
                checked_ts=now if checked else None,
            )
        items.append(item)

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "list"
    return GroceryList(slug=slug, title=title or "List", items=items)


# ---------------------------------------------------------------------------
# Archive serialization/parsing (PLAN §4.6)
# ---------------------------------------------------------------------------
#
# The archive file ``archive/<slug>.md`` is an append-only, human-readable log
# of items cleared out of the live list. Each entry reuses the same per-item
# metadata comment as the live list, plus two extra fields:
#   ``arch:<archived_ts>``  when the item left the live list
#   ``reason:<reason>``     why (``cleared`` for clear-checked)
# Entries are rendered newest-first for browsing; parsing is order-independent
# because identity comes from the metadata (id + arch timestamp).


def serialize_archive(
    title: str,
    archived: list[ArchivedItem],
) -> str:
    """Serialize a list's archive to Markdown (newest entries first)."""
    entries = sorted(
        archived, key=lambda a: (a.archived_ts, a.item.id), reverse=True
    )
    lines: list[str] = [f"# {title} \u2014 Archive", ""]
    for entry in entries:
        item = entry.item
        text = _render_item_text(item)
        meta = _encode_meta(item)
        meta = f"{meta} arch:{entry.archived_ts} reason:{entry.reason}"
        # Archived items are, by definition, previously-checked; render as [x].
        lines.append(f"- [x] {text} <!-- {meta} -->")
    return "\n".join(lines).rstrip("\n") + "\n"


def parse_archive(text: str) -> tuple[str, list[ArchivedItem]]:
    """Parse an archive Markdown file into (title, list[ArchivedItem]).

    Title is taken from the ``# <title> — Archive`` heading (the trailing
    ``— Archive`` suffix is stripped). Entries without an ``id`` in metadata are
    skipped (an archive line is meaningless without its structured record).
    """
    title = ""
    archived: list[ArchivedItem] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")

        h1 = _H1_RE.match(line)
        if h1 and not title:
            title = h1.group("title").strip()
            # Strip the localized/en ' — Archive' suffix if present.
            title = re.sub(r"\s*\u2014\s*Archive\s*$", "", title).strip()
            continue

        item_match = _ITEM_RE.match(line)
        if not item_match:
            continue

        _visible, meta = _strip_meta_from_rest(item_match.group("rest"))
        if not meta or "id" not in meta:
            continue

        category = meta.get("cat")
        if category in (None, "-", ""):
            category = None
        else:
            category = unquote(category)
        added_by = meta.get("by")
        if added_by in (None, "-"):
            added_by = ""
        item = Item(
            id=meta["id"],
            name=_visible_to_name_qty(_visible)[0] or _visible,
            category=category,
            qty=_qty_from_meta(meta.get("qty")),
            checked=True,
            added_by=added_by or "",
            created_ts=meta.get("ts") or utcnow_iso(),
            updated_ts=meta.get("upd") or meta.get("ts") or utcnow_iso(),
            checked_ts=meta.get("checked_ts"),
        )
        archived.append(
            ArchivedItem(
                item=item,
                archived_ts=meta.get("arch") or item.updated_ts,
                reason=meta.get("reason") or "cleared",
            )
        )

    return title, archived
