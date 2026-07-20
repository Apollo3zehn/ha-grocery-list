"""Pure repository <-> model (de)serialization and merge orchestration.

This module is deliberately free of Home Assistant and git dependencies so it
can be unit-tested in isolation. It knows the on-disk *layout* of the synced
repo (which files exist and how they encode state) and how to:

- load a full :class:`RepoState` from a mapping of ``path -> bytes`` (the
  working tree, or a set of blobs read at a commit),
- serialize a :class:`RepoState` back to a ``path -> bytes`` mapping for the
  git backend to write,
- perform the whole-repo semantic 3-way merge (lists + categories + op-log) by
  delegating to the existing pure merge functions.

The git backend (``git_backend.py``) and the async coordinator
(``coordinator.py``) sit above this and handle transport + scheduling. Keeping
this layer pure is what makes the sync logic testable and VCS-agnostic
(PLAN §2).

Repo layout (see PLAN §9 and ``const.py``):
- ``lists/<slug>.md``              human-readable list (live items only)
- ``.grocery/tombstones/<slug>.json`` per-list tombstones (kept out of the md)
- ``.grocery/categories.json``     user-managed categories + tombstones
- ``.grocery/oplog.jsonl``         shared append-only op-log
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from . import markdown_io
from .categories import CategorySet, merge_category_sets
from .const import (
    ARCHIVE_DIR,
    CATEGORIES_FILE,
    LIST_TOMBSTONES_FILE,
    LISTS_DIR,
    OPLOG_FILE,
    TOMBSTONES_DIR,
)
from .merge import merge as merge_list
from .models import ArchivedItem, ListState, Tombstone
from .oplog import OpLog, merge_oplogs

_SLUG_FROM_PATH = re.compile(r"^lists/(?P<slug>.+)\.md$")
_TOMB_FROM_PATH = re.compile(r"^\.grocery/tombstones/(?P<slug>.+)\.json$")
_ARCHIVE_FROM_PATH = re.compile(r"^archive/(?P<slug>.+)\.md$")


def _list_path(slug: str) -> str:
    return f"{LISTS_DIR}/{slug}.md"


def _tombstones_path(slug: str) -> str:
    return f"{TOMBSTONES_DIR}/{slug}.json"


def _archive_path(slug: str) -> str:
    return f"{ARCHIVE_DIR}/{slug}.md"


@dataclass(slots=True)
class RepoState:
    """The complete mergeable state of the synced repository.

    ``lists`` maps slug -> :class:`ListState` (items + tombstones). ``categories``
    is the user-managed :class:`CategorySet`. ``oplog`` is the shared op-log.
    """

    lists: dict[str, ListState] = field(default_factory=dict)
    categories: CategorySet = field(default_factory=CategorySet)
    oplog: OpLog = field(default_factory=OpLog)
    # Per-slug append-only archive of cleared items (PLAN §4.6). Kept separate
    # from ListState so the semantic list merge stays untouched; archives merge
    # by simple union on their stable key.
    archives: dict[str, list[ArchivedItem]] = field(default_factory=dict)
    # List-level tombstones (deleted whole lists), keyed by slug. Kept in a
    # central sidecar (``.grocery/list_tombstones.json``) so a list deletion on
    # one device isn't resurrected by another that still carries the markdown;
    # merged by last-writer-wins vs. any surviving list content (mirrors the
    # category tombstone rule).
    list_tombstones: dict[str, Tombstone] = field(default_factory=dict)

    # -- loading ------------------------------------------------------------

    @classmethod
    def from_files(cls, files: dict[str, bytes]) -> "RepoState":
        """Build a RepoState from a ``path -> bytes`` mapping.

        Unknown files are ignored. Missing files default to empty. Tombstone
        sidecars are matched to their list by slug; a tombstone file with no
        corresponding md still produces a ListState (title falls back to slug).
        """
        # Decode helper.
        def _text(path: str) -> str | None:
            data = files.get(path)
            return data.decode("utf-8") if data is not None else None

        # First pass: parse list markdown files.
        lists: dict[str, ListState] = {}
        tombstone_blobs: dict[str, list[Tombstone]] = {}
        archives: dict[str, list[ArchivedItem]] = {}

        for path, data in files.items():
            slug_match = _SLUG_FROM_PATH.match(path)
            if slug_match:
                slug = slug_match.group("slug")
                glist = markdown_io.parse(data.decode("utf-8"))
                glist.slug = slug  # filename is authoritative for slug
                lists[slug] = ListState.from_list(glist)
                continue
            tomb_match = _TOMB_FROM_PATH.match(path)
            if tomb_match:
                slug = tomb_match.group("slug")
                raw = json.loads(data.decode("utf-8") or "[]")
                tombstone_blobs[slug] = [
                    Tombstone.from_dict(d) for d in raw
                ]
                continue
            arch_match = _ARCHIVE_FROM_PATH.match(path)
            if arch_match:
                slug = arch_match.group("slug")
                _title, entries = markdown_io.parse_archive(
                    data.decode("utf-8")
                )
                archives[slug] = entries

        # Attach tombstones to their list (creating a bare ListState if the md
        # is absent, e.g. a fully-cleared list).
        for slug, tombs in tombstone_blobs.items():
            state = lists.get(slug)
            if state is None:
                state = ListState(slug=slug, title=slug)
                lists[slug] = state
            state.tombstones = {t.id: t for t in tombs}

        categories = CategorySet.from_json(_text(CATEGORIES_FILE) or "")
        oplog = OpLog.parse(_text(OPLOG_FILE) or "")

        # Central list-level tombstones (deleted whole lists).
        list_tombstones: dict[str, Tombstone] = {}
        raw_lt = _text(LIST_TOMBSTONES_FILE)
        if raw_lt and raw_lt.strip():
            for d in json.loads(raw_lt):
                tomb = Tombstone.from_dict(d)
                list_tombstones[tomb.id] = tomb

        return cls(
            lists=lists,
            categories=categories,
            oplog=oplog,
            archives=archives,
            list_tombstones=list_tombstones,
        )

    # -- serialization ------------------------------------------------------

    def to_files(
        self,
        *,
        category_labels_locale: str = "en",
    ) -> dict[str, bytes]:
        """Serialize to a ``path -> bytes`` mapping for the git backend.

        List markdown is rendered using the current category order/labels so the
        file on the host is grouped and readable. Tombstones are written to
        their JSON sidecars. Categories and the op-log are written whole.
        """
        out: dict[str, bytes] = {}

        order = self.categories.order_ids()
        labels = self.categories.labels_map(category_labels_locale)

        for slug, state in self.lists.items():
            # A tombstoned (deleted) list is not written back to disk.
            if slug in self.list_tombstones:
                continue
            glist = state.to_list()
            glist.slug = slug
            md = markdown_io.serialize(
                glist,
                category_order=order,
                category_labels=labels,
            )
            out[_list_path(slug)] = md.encode("utf-8")

            tombs = list(state.tombstones.values())
            out[_tombstones_path(slug)] = (
                json.dumps(
                    [t.to_dict() for t in tombs], indent=2, sort_keys=True
                )
                + "\n"
            ).encode("utf-8")

        # Archive files (one per slug that has any archived entries). Rendered
        # newest-first for browsing; the list title (if known) heads the file.
        for slug, entries in self.archives.items():
            if not entries:
                continue
            title = self.lists[slug].title if slug in self.lists else slug
            md = markdown_io.serialize_archive(title, entries)
            out[_archive_path(slug)] = md.encode("utf-8")

        out[CATEGORIES_FILE] = self.categories.to_json().encode("utf-8")
        out[OPLOG_FILE] = self.oplog.serialize().encode("utf-8")
        out[LIST_TOMBSTONES_FILE] = (
            json.dumps(
                [t.to_dict() for t in self.list_tombstones.values()],
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
        return out


def merge_repo_states(
    base: RepoState, ours: RepoState, theirs: RepoState
) -> RepoState:
    """Whole-repo semantic 3-way merge (PLAN §3), delegating per subsystem.

    - Lists: union of slugs; per slug, :func:`merge.merge` on the three
      ``ListState`` snapshots (empty ListState for missing sides).
    - Categories: :func:`categories.merge_category_sets`.
    - Op-log: :func:`oplog.merge_oplogs` (append-only union).
    """
    all_slugs = set(base.lists) | set(ours.lists) | set(theirs.lists)
    merged_lists: dict[str, ListState] = {}
    for slug in all_slugs:
        b = base.lists.get(slug) or ListState(slug=slug, title=slug)
        o = ours.lists.get(slug) or ListState(slug=slug, title=b.title)
        t = theirs.lists.get(slug) or ListState(slug=slug, title=b.title)
        merged_lists[slug] = merge_list(b, o, t)

    merged_categories = merge_category_sets(
        base.categories, ours.categories, theirs.categories
    )
    merged_oplog = merge_oplogs(base.oplog, ours.oplog, theirs.oplog)
    merged_archives = _merge_archives(base, ours, theirs)
    merged_list_tombs = _merge_list_tombstones(base, ours, theirs, merged_lists)

    return RepoState(
        lists=merged_lists,
        categories=merged_categories,
        oplog=merged_oplog,
        archives=merged_archives,
        list_tombstones=merged_list_tombs,
    )


def _merge_list_tombstones(
    base: RepoState,
    ours: RepoState,
    theirs: RepoState,
    merged_lists: dict[str, ListState],
) -> dict[str, Tombstone]:
    """Merge list-level tombstones, resolving delete-vs-edit per slug (PLAN §3).

    Union of tombstoned slugs across sides; the newest tombstone wins. A list is
    resurrected (tombstone dropped) only if the merged list has a live item with
    an ``updated_ts`` strictly newer than the deletion — i.e. someone actively
    re-populated it after the delete. Otherwise the deletion stands and the
    merged list's live items are cleared so the deletion actually takes effect.
    """
    all_slugs = (
        set(base.list_tombstones)
        | set(ours.list_tombstones)
        | set(theirs.list_tombstones)
    )
    merged: dict[str, Tombstone] = {}
    for slug in all_slugs:
        tombs = [
            t
            for t in (
                ours.list_tombstones.get(slug),
                theirs.list_tombstones.get(slug),
                base.list_tombstones.get(slug),
            )
            if t is not None
        ]
        newest = max(tombs, key=lambda t: t.deleted_ts)
        lstate = merged_lists.get(slug)
        newest_edit = ""
        if lstate is not None and lstate.items:
            newest_edit = max(it.updated_ts for it in lstate.items.values())
        if newest_edit > newest.deleted_ts:
            # Active re-population after deletion -> resurrect the list.
            continue
        merged[slug] = newest
        # Enforce the deletion: drop any lingering live items so the list is
        # empty (its markdown won't be written while tombstoned).
        if lstate is not None:
            lstate.items.clear()
    return merged


def _merge_archives(
    base: RepoState, ours: RepoState, theirs: RepoState
) -> dict[str, list[ArchivedItem]]:
    """Union per-slug archives by stable key (append-only, PLAN §4.6).

    The archive is an append-only log, so merging is a simple set-union of
    entries across all three sides keyed by :attr:`ArchivedItem.key` (item id +
    archived_ts). Auto-purge is applied separately (by the coordinator) and
    propagates as the absence of entries plus ``purged`` tombstones; since purge
    runs deterministically by age it converges without needing 3-way logic
    here. Entries are returned sorted newest-first for stable serialization.
    """
    all_slugs = set(base.archives) | set(ours.archives) | set(theirs.archives)
    merged: dict[str, list[ArchivedItem]] = {}
    for slug in all_slugs:
        by_key: dict[str, ArchivedItem] = {}
        for side in (base, ours, theirs):
            for entry in side.archives.get(slug, []):
                by_key.setdefault(entry.key, entry)
        if by_key:
            merged[slug] = sorted(
                by_key.values(),
                key=lambda a: (a.archived_ts, a.item.id),
                reverse=True,
            )
    return merged
