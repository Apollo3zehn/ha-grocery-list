"""Markdown serialization/parsing for grocery lists.

A list file (``lists/<slug>.md``) is a clean, human-readable rendering with no
hidden metadata: item identity is ``(category, name)`` and everything needed to
reconstruct an item is visible on the page. The Markdown is a *projection* of
the model, and this module round-trips losslessly for the persisted fields
(name, category, qty, checked).

Layout rules:
- ``# <title>`` is the top-level heading.
- Each category is a ``## <name>`` section; items are ``- [ ]``/``- [x]``.
- Categories are ordered alphabetically by name; items with a ``None``
  category render last under an ``uncategorized_label`` section (caller-
  provided, localized). Within a section, unchecked items come first and
  checked items sink to the bottom.
- An item line is ``- [ ] Name`` or ``- [x] Name`` with an optional
  `` ×<value> <unit>`` quantity suffix (integers rendered without ``.0``).

The parser maps a ``## <label>`` header back to a category, translating the
uncategorized label back to ``None`` so round-trips are lossless.
"""

from __future__ import annotations

import re

from .models import GroceryList, Item, Quantity

_ITEM_RE = re.compile(r"^\s*-\s*\[(?P<check>[ xX])\]\s*(?P<rest>.*?)\s*$")
_H1_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$")
_H2_RE = re.compile(r"^##\s+(?P<label>.+?)\s*$")


def _fmt_value(value: float) -> str:
    """Render a numeric quantity value, integers without a trailing ``.0``."""
    return str(int(value)) if float(value).is_integer() else str(value)


def _render_item_text(item: Item) -> str:
    """Render the visible portion of an item line (without the checkbox)."""
    text = item.name
    if item.qty is not None:
        text = f"{text} \u00d7{_fmt_value(item.qty.value)} {item.qty.unit}"
    return text


def _parse_name_qty(visible: str) -> tuple[str, Quantity | None]:
    """Parse ``Name ×VALUE UNIT`` visible text into ``(name, Quantity|None)``."""
    m = re.search(r"\s\u00d7\s*(\d+(?:\.\d+)?)\s+(\S+)\s*$", visible)
    if not m:
        return visible.strip(), None
    name = visible[: m.start()].strip()
    try:
        qty = Quantity(value=float(m.group(1)), unit=m.group(2))
    except ValueError:
        return visible.strip(), None
    return name, qty


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def serialize(
    glist: GroceryList,
    *,
    uncategorized_label: str = "Uncategorized",
) -> str:
    """Serialize a GroceryList to clean Markdown text."""
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
        items_sorted = sorted(
            buckets[key],
            key=lambda it: (it.checked, it.name.lower()),
        )
        label = key if key else uncategorized_label
        lines.append(f"## {label}")
        for item in items_sorted:
            box = "x" if item.checked else " "
            lines.append(f"- [{box}] {_render_item_text(item)}")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def parse(text: str, *, uncategorized_label: str = "Uncategorized") -> GroceryList:
    """Parse Markdown text into a GroceryList.

    The slug is not encoded in the file; callers set it from the filename. Here
    we default slug to a slugified title, which callers typically override.
    A ``## <label>`` header sets the current category for the items beneath it;
    a header equal to ``uncategorized_label`` maps back to ``None``.
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
            label = h2.group("label").strip()
            current_category = None if label == uncategorized_label else label
            continue

        item_match = _ITEM_RE.match(line)
        if not item_match:
            continue

        checked = item_match.group("check").lower() == "x"
        name, qty = _parse_name_qty(item_match.group("rest"))
        items.append(
            Item(
                name=name,
                category=current_category,
                qty=qty,
                checked=checked,
            )
        )

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "list"
    return GroceryList(slug=slug, title=title or "List", items=items)
