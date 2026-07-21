"""Pure repository <-> model (de)serialization and merge orchestration.

This module is deliberately free of Home Assistant and git dependencies so it
can be unit-tested in isolation. It knows the on-disk *layout* of the synced
repo (which files exist and how they encode state) and how to:

- load a full :class:`RepoState` from a mapping of ``path -> bytes`` (the
  working tree, or a set of blobs read at a commit),
- serialize a :class:`RepoState` back to a ``path -> bytes`` mapping for the
  git backend to write,
- perform the whole-repo semantic 3-way merge (lists) by delegating to the
  pure merge functions.

There is no sync metadata on disk: no tombstones, timestamps, or ids. Deletions
are detected structurally by the 3-way merge against the git merge-base. The
archive of cleared items lives in an HA ``Store`` (owned by the coordinator),
not in git. Categories are derived implicitly from the live items' ``category``
name field, so there is nothing category-related to load, serialize, or merge.

The undo/redo op-log is intentionally NOT part of ``RepoState``: it is an
in-memory-only, per-runtime concern owned by the coordinator.

Repo layout:
- ``lists/<slug>.md``   human-readable list (the only tracked files)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import markdown_io
from .merge import merge as merge_list
from .models import GroceryList


def _norm_prefix(lists_path: str) -> str:
    """Normalize a configured lists path to a clean relative prefix.

    Empty / "." / "/" all mean the repo root. Leading/trailing slashes are
    stripped so ``/foo/bar/`` and ``foo/bar`` are equivalent.
    """
    return (lists_path or "").strip().strip("/")


def _slug_regex(lists_path: str) -> re.Pattern[str]:
    """Regex matching ``<prefix>/<slug>.md`` (or ``<slug>.md`` at root).

    ``slug`` excludes ``/`` so only files directly in the lists directory are
    treated as lists (nested files are ignored).
    """
    prefix = _norm_prefix(lists_path)
    if prefix:
        return re.compile(rf"^{re.escape(prefix)}/(?P<slug>[^/]+)\.md$")
    return re.compile(r"^(?P<slug>[^/]+)\.md$")


def _list_path(slug: str, lists_path: str = "") -> str:
    prefix = _norm_prefix(lists_path)
    return f"{prefix}/{slug}.md" if prefix else f"{slug}.md"


@dataclass(slots=True)
class RepoState:
    """The complete mergeable state of the synced repository.

    ``lists`` maps slug -> :class:`GroceryList`. The set of categories is not
    stored; it is derived from the items' ``category`` names.
    """

    lists: dict[str, GroceryList] = field(default_factory=dict)

    # -- loading ------------------------------------------------------------

    @classmethod
    def from_files(
        cls, files: dict[str, bytes], lists_path: str = ""
    ) -> "RepoState":
        """Build a RepoState from a ``path -> bytes`` mapping.

        Only ``<lists_path>/<slug>.md`` files are considered (``<slug>.md`` at
        the repo root when ``lists_path`` is empty); anything else is ignored.
        The filename is authoritative for each list's slug.
        """
        slug_re = _slug_regex(lists_path)
        lists: dict[str, GroceryList] = {}
        for path, data in files.items():
            slug_match = slug_re.match(path)
            if not slug_match:
                continue
            slug = slug_match.group("slug")
            glist = markdown_io.parse(data.decode("utf-8"))
            glist.slug = slug  # filename is authoritative for slug
            lists[slug] = glist
        return cls(lists=lists)

    # -- serialization ------------------------------------------------------

    def to_files(self, lists_path: str = "") -> dict[str, bytes]:
        """Serialize to a ``path -> bytes`` mapping for the git backend.

        Each list is rendered to clean Markdown grouped by category name and
        placed under ``lists_path`` (repo root when empty).
        """
        out: dict[str, bytes] = {}
        for slug, glist in self.lists.items():
            glist.slug = slug
            md = markdown_io.serialize(glist)
            out[_list_path(slug, lists_path)] = md.encode("utf-8")
        return out


def merge_repo_states(
    base: RepoState, ours: RepoState, theirs: RepoState
) -> RepoState:
    """Whole-repo semantic 3-way merge, delegating per list.

    Lists: union of slugs; per slug, :func:`merge.merge` on the three
    ``GroceryList`` snapshots (empty ``GroceryList`` for missing sides). A slug
    present in ``base`` but missing on a side is a list deletion, honored the
    same way item deletions are: if the surviving side is unchanged from base
    the list is dropped; otherwise the surviving edits win.
    """
    all_slugs = set(base.lists) | set(ours.lists) | set(theirs.lists)
    merged_lists: dict[str, GroceryList] = {}
    for slug in all_slugs:
        in_base = slug in base.lists
        o = ours.lists.get(slug)
        t = theirs.lists.get(slug)

        if o is not None and t is not None:
            b = base.lists.get(slug) or GroceryList(slug=slug, title=o.title)
            merged_lists[slug] = merge_list(b, o, t)
        elif o is not None or t is not None:
            single = o if o is not None else t
            assert single is not None
            if in_base:
                base_list = base.lists[slug]
                # List deleted on one side. Honor the deletion unless the
                # surviving side changed it (title or items) vs base.
                if (
                    single.title == base_list.title
                    and _items_equal(single, base_list)
                ):
                    continue
                merged_lists[slug] = single
            else:
                merged_lists[slug] = single
        # absent on both -> nothing

    return RepoState(lists=merged_lists)


def _items_equal(a: GroceryList, b: GroceryList) -> bool:
    """Return True if two lists have the same set of items (by value)."""
    ak = {it.key: it for it in a.items}
    bk = {it.key: it for it in b.items}
    return ak == bk
