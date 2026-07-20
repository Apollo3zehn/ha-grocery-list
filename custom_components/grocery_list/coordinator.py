"""Async sync coordinator (PLAN §5, §2, §6).

This is the orchestration layer that ties everything together at runtime:

- Holds the in-memory :class:`RepoState` (lists, categories, op-log).
- Owns the :class:`GitBackend` and runs every blocking git call in an executor
  (dulwich/paramiko are synchronous; HA is asyncio — PLAN §2 runtime note).
- Implements the sync cadence (PLAN §5):
    * **debounced push** ``push_debounce_seconds`` after the last local change,
    * **scheduled pull** every ``pull_interval_seconds``,
    * **pull on HA start**, and **pull before every push**.
- Runs the sync/merge flow: fetch -> if remote advanced beyond
  ``last_synced_commit`` load base blobs + theirs + ours -> semantic 3-way
  merge (``repo_state.merge_repo_states``) -> serialize -> 2-parent merge commit
  -> push -> advance ``last_synced_commit``.
- Tracks and surfaces the **sync state** (synced/pending/syncing/offline/error).
- Persists ``last_synced_commit`` via HA ``Store``.
- Exposes high-level mutation methods (add/update/check/delete item, category
  CRUD, clear-checked, undo/redo) that mutate the model, append op-log entries,
  commit, and schedule a push. These are what the websocket API (Phase 9) calls.

The heavy, correctness-critical logic (serialization + merge) lives in the pure,
fully-tested ``repo_state``/``merge``/``oplog``/``categories`` modules; this file
is intentionally the thin, HA-and-IO-bound shell around them.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .categories import CategorySet
from .const import (
    CONF_AUTH_METHOD,
    CONF_ARCHIVE_RETENTION,
    CONF_BRANCH,
    CONF_HTTPS_TOKEN,
    CONF_IDENTITY,
    CONF_PULL_INTERVAL,
    CONF_PUSH_DEBOUNCE,
    CONF_REPO_URL,
    CONF_SSH_KEY,
    CONF_SSH_KEY_PATH,
    CONF_SYNC_ENABLED,
    DEFAULT_ARCHIVE_RETENTION,
    DEFAULT_BRANCH,
    DEFAULT_PULL_INTERVAL,
    DEFAULT_PUSH_DEBOUNCE,
    DOMAIN,
    LIST_TOMBSTONES_FILE,
    OPLOG_FILE,
    SYNC_ERROR,
    SYNC_LOCAL,
    SYNC_OFFLINE,
    SYNC_PENDING,
    SYNC_SYNCED,
    SYNC_SYNCING,
)
from .git_backend import (
    GitAuthError,
    GitBackend,
    GitBackendError,
    GitCredentials,
)
from .models import (
    ArchivedItem,
    Item,
    ListState,
    Quantity,
    Tombstone,
    new_id,
    utcnow_iso,
)
from .oplog import ENTITY_CATEGORY, ENTITY_ITEM, ENTITY_LIST, Op, make_action_op
from .repo_state import RepoState, merge_repo_states

_LOGGER = logging.getLogger(__name__)


class GroceryCoordinator:
    """Owns runtime state and the git sync lifecycle for one config entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.identity: str = entry.data[CONF_IDENTITY]
        self._work_dir = hass.config.path(f".storage/{DOMAIN}/{entry.entry_id}")
        self._store: Store = Store(
            hass, 1, f"{DOMAIN}.{entry.entry_id}.sync"
        )
        self._backend: GitBackend | None = None
        self.state = RepoState()
        self.sync_state: str = SYNC_OFFLINE
        self.last_synced_commit: str | None = None

        # Concurrency + scheduling primitives.
        self._sync_lock = asyncio.Lock()
        self._push_unsub: Callable[[], None] | None = None
        self._pull_unsub: Callable[[], None] | None = None
        self._local_write_unsub: Callable[[], None] | None = None
        self._listeners: list[Callable[[], None]] = []

    # -- option helpers -----------------------------------------------------

    @property
    def sync_enabled(self) -> bool:
        """Whether this instance syncs to a git remote (vs local-only).

        Defaults to True for backward compatibility with entries created
        before local-only mode existed (they always had a git remote).
        """
        return self.entry.data.get(CONF_SYNC_ENABLED, True)

    @property
    def _push_debounce(self) -> int:
        return self.entry.options.get(CONF_PUSH_DEBOUNCE, DEFAULT_PUSH_DEBOUNCE)

    @property
    def _pull_interval(self) -> int:
        return self.entry.options.get(CONF_PULL_INTERVAL, DEFAULT_PULL_INTERVAL)

    @property
    def _archive_retention_days(self) -> int:
        return self.entry.options.get(
            CONF_ARCHIVE_RETENTION, DEFAULT_ARCHIVE_RETENTION
        )

    # -- lifecycle ----------------------------------------------------------

    def _require_backend(self) -> GitBackend:
        if self._backend is None:
            raise GitBackendError("Git backend not initialized")
        return self._backend

    def _build_backend(self) -> GitBackend:
        data = self.entry.data
        creds = GitCredentials(
            method=data[CONF_AUTH_METHOD],
            ssh_key_data=(data.get(CONF_SSH_KEY) or "") or None,
            ssh_key_path=(data.get(CONF_SSH_KEY_PATH) or "") or None,
            https_token=(data.get(CONF_HTTPS_TOKEN) or "") or None,
        )
        return GitBackend(
            self._work_dir,
            data[CONF_REPO_URL],
            creds,
            data.get(CONF_BRANCH, DEFAULT_BRANCH),
        )

    async def async_setup(self) -> None:
        """Clone-or-open the repo, load state, and start timers (PLAN §5).

        In local-only mode there is no git remote: we ensure the work dir
        exists, load any previously-persisted state files, purge archives, and
        return without a backend or sync timers.
        """
        if not self.sync_enabled:
            await self._async_setup_local()
            return

        stored = await self._store.async_load()
        if stored:
            self.last_synced_commit = stored.get("last_synced_commit")

        self._backend = self._build_backend()

        backend = self._require_backend()

        def _open_or_clone() -> None:
            import os

            if os.path.isdir(os.path.join(self._work_dir, ".git")):
                backend.open()
            else:
                os.makedirs(self._work_dir, exist_ok=True)
                backend.clone()

        try:
            await self.hass.async_add_executor_job(_open_or_clone)
        except GitAuthError as err:
            self.sync_state = SYNC_ERROR
            raise
        except GitBackendError:
            # Offline is tolerable: we can still work locally if a prior clone
            # exists; otherwise re-raise to fail setup.
            self.sync_state = SYNC_OFFLINE
            raise

        await self._async_load_working_state()

        # Purge stale archive entries on startup (PLAN §4.6).
        self.async_purge_archives()

        # Pull on HA start (PLAN §5), then start the periodic pull timer.
        await self.async_sync()
        self._pull_unsub = async_track_time_interval(
            self.hass,
            self._handle_scheduled_pull,
            _as_timedelta(self._pull_interval),
        )

    async def _async_setup_local(self) -> None:
        """Set up a local-only instance: load persisted files, no git/timers."""
        import os

        def _ensure_dir() -> None:
            os.makedirs(self._work_dir, exist_ok=True)

        await self.hass.async_add_executor_job(_ensure_dir)
        await self._async_load_working_state()
        self.async_purge_archives()
        self.sync_state = SYNC_LOCAL
        self._notify()

    async def async_shutdown(self) -> None:
        """Cancel timers and flush a final push/write if changes are pending."""
        if self._pull_unsub is not None:
            self._pull_unsub()
            self._pull_unsub = None
        if self._push_unsub is not None:
            self._push_unsub()
            self._push_unsub = None
        if not self.sync_enabled:
            # Flush any debounced local write so nothing is lost on restart.
            if self._local_write_unsub is not None:
                self._local_write_unsub()
                self._local_write_unsub = None
            await self._async_write_local_state()
            return
        if self.sync_state == SYNC_PENDING:
            await self.async_sync()

    # -- state loading ------------------------------------------------------

    async def _async_load_working_state(self) -> None:
        """Load the working-tree files into an in-memory RepoState."""

        def _read_all() -> dict[str, bytes]:
            import os

            files: dict[str, bytes] = {}
            for sub in ("lists", ".grocery", "archive"):
                base = os.path.join(self._work_dir, sub)
                if not os.path.isdir(base):
                    continue
                for root, _dirs, names in os.walk(base):
                    for name in names:
                        full = os.path.join(root, name)
                        rel = os.path.relpath(full, self._work_dir)
                        with open(full, "rb") as fh:
                            files[rel.replace(os.sep, "/")] = fh.read()
            return files

        files = await self.hass.async_add_executor_job(_read_all)
        self.state = RepoState.from_files(files)

    # -- change notification ------------------------------------------------

    @callback
    def async_add_listener(self, cb: Callable[[], None]) -> Callable[[], None]:
        """Register a listener (websocket API) for state/sync changes."""
        self._listeners.append(cb)

        def _remove() -> None:
            if cb in self._listeners:
                self._listeners.remove(cb)

        return _remove

    @callback
    def _notify(self) -> None:
        for cb in list(self._listeners):
            cb()

    @callback
    def _set_sync_state(self, state: str) -> None:
        if state != self.sync_state:
            self.sync_state = state
            self._notify()

    # -- push scheduling ----------------------------------------------------

    @callback
    def _schedule_push(self) -> None:
        """(Re)arm the debounce timer; every local change calls this."""
        self._set_sync_state(SYNC_PENDING)
        if self._push_unsub is not None:
            self._push_unsub()
        self._push_unsub = async_call_later(
            self.hass, self._push_debounce, self._handle_debounced_push
        )

    async def _handle_debounced_push(self, _now) -> None:
        self._push_unsub = None
        await self.async_sync()
    async def _handle_scheduled_pull(self, _now) -> None:
        await self.async_sync()

    # -- local-only persistence --------------------------------------------

    @callback
    def _schedule_local_write(self) -> None:
        """(Re)arm a short debounce to persist state to disk (local mode).

        Mirrors :meth:`_schedule_push` but there is no remote; we simply
        serialize the model to plain files in the work dir so it survives a
        restart. A short 2s debounce coalesces bursts of edits.
        """
        if self._local_write_unsub is not None:
            self._local_write_unsub()
        self._local_write_unsub = async_call_later(
            self.hass, 2, self._handle_local_write
        )

    async def _handle_local_write(self, _now) -> None:
        self._local_write_unsub = None
        await self._async_write_local_state()

    async def _async_write_local_state(self) -> None:
        """Serialize the model to the work dir and prune stale files.

        Writes the same file layout as the git working tree
        (``RepoState.to_files``) so local and synced modes share the exact
        same on-disk format and the same loader (``_async_load_working_state``).
        Files no longer present in the model are removed so deletions persist.
        """
        files = self.state.to_files()

        def _write() -> None:
            import os

            wanted = set()
            for rel, data in files.items():
                full = os.path.join(self._work_dir, rel)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "wb") as fh:
                    fh.write(data)
                wanted.add(os.path.normpath(full))
            # Prune stale files under our managed subdirs.
            for sub in ("lists", ".grocery", "archive"):
                base = os.path.join(self._work_dir, sub)
                if not os.path.isdir(base):
                    continue
                for root, _dirs, names in os.walk(base):
                    for name in names:
                        full = os.path.normpath(os.path.join(root, name))
                        if full not in wanted:
                            os.remove(full)

        await self.hass.async_add_executor_job(_write)

    # -- the sync flow ------------------------------------------------------

    async def async_sync(self) -> None:
        """Fetch, semantic-merge if remote advanced, commit, and push.

        This single method implements the whole flow (PLAN §5). It is guarded by
        a lock so scheduled pulls and debounced pushes can't interleave.
        """
        if self._backend is None:
            return
        async with self._sync_lock:
            self._set_sync_state(SYNC_SYNCING)
            try:
                await self._async_commit_working_tree()
                remote_sha = await self.hass.async_add_executor_job(
                    self._backend.fetch
                )
                if remote_sha and remote_sha != self.last_synced_commit:
                    await self._async_merge_with_remote(remote_sha)

                await self.hass.async_add_executor_job(self._backend.push)

                head = await self.hass.async_add_executor_job(
                    self._backend.head_commit_sha
                )
                await self._async_set_last_synced(head)
                self._set_sync_state(SYNC_SYNCED)
            except GitAuthError:
                _LOGGER.exception("Grocery List: authentication failed")
                self._set_sync_state(SYNC_ERROR)
            except GitBackendError:
                _LOGGER.warning("Grocery List: sync failed (offline?)")
                self._set_sync_state(SYNC_OFFLINE)
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Grocery List: unexpected sync error")
                self._set_sync_state(SYNC_ERROR)

    async def _async_commit_working_tree(self) -> None:
        """Serialize current model to files, stage, and commit if changed."""
        files = self.state.to_files()
        backend = self._require_backend()

        def _write_and_commit() -> str | None:
            backend.write_files(files)
            # do_commit with an unchanged tree raises; guard by comparing.
            try:
                return backend.commit(
                    f"grocery: update ({self.identity})",
                    self._author(),
                )
            except Exception as err:  # noqa: BLE001
                # Nothing to commit is not an error.
                if "nothing to commit" in str(err).lower():
                    return None
                raise

        await self.hass.async_add_executor_job(_write_and_commit)

    async def _async_merge_with_remote(self, remote_sha: str) -> None:
        """Load base + theirs blobs, merge with ours, write merged, merge-commit."""
        base_commit = self.last_synced_commit
        backend = self._require_backend()

        def _read_side(commit_sha: str | None) -> dict[str, bytes]:
            if not commit_sha:
                return {}
            files: dict[str, bytes] = {}
            for rel in self._tracked_paths():
                data = backend.read_blob_at(commit_sha, rel)
                if data is not None:
                    files[rel] = data
            return files

        base_files = await self.hass.async_add_executor_job(
            _read_side, base_commit
        )
        their_files = await self.hass.async_add_executor_job(
            _read_side, remote_sha
        )

        base_state = RepoState.from_files(base_files)
        their_state = RepoState.from_files(their_files)
        merged = merge_repo_states(base_state, self.state, their_state)
        self.state = merged

        merged_files = merged.to_files()

        def _write_merge_commit() -> None:
            backend.write_files(merged_files)
            backend.merge_commit(
                f"grocery: merge remote ({self.identity})",
                self._author(),
                remote_sha,
            )

        await self.hass.async_add_executor_job(_write_merge_commit)
        self._notify()

    def _tracked_paths(self) -> list[str]:
        """All repo-relative paths our model serializes to (for blob reads)."""
        paths: list[str] = [
            f"lists/{slug}.md" for slug in self.state.lists
        ]
        paths += [
            f".grocery/tombstones/{slug}.json" for slug in self.state.lists
        ]
        paths.append(".grocery/categories.json")
        paths.append(OPLOG_FILE)
        paths.append(LIST_TOMBSTONES_FILE)
        return paths

    async def _async_set_last_synced(self, sha: str | None) -> None:
        self.last_synced_commit = sha
        await self._store.async_save(
            {"last_synced_commit": sha, "saved_ts": utcnow_iso()}
        )

    def _author(self) -> str:
        return f"{self.identity} <grocery@{self.identity}.local>"

    # -- op-log helper ------------------------------------------------------

    def _record_and_schedule(self, op: Op) -> None:
        """Append an op to the shared log and arm a debounced push/write."""
        self.state.oplog.append(op)
        self._notify()
        if self.sync_enabled:
            self._schedule_push()
        else:
            self._schedule_local_write()

    # -- list/item mutations (called by websocket API) ---------------------

    def _ensure_list(self, slug: str, title: str | None = None) -> ListState:
        state = self.state.lists.get(slug)
        if state is None:
            state = ListState(slug=slug, title=title or slug)
            self.state.lists[slug] = state
        return state

    def _unique_slug(self, base: str) -> str:
        """Return a repo-unique slug derived from ``base`` (title or slug).

        Slugs are the on-disk file stems (``lists/<slug>.md``) and must be
        filesystem-safe and unique. We lowercase, keep alphanumerics/hyphens,
        collapse the rest to hyphens, then disambiguate against existing lists
        AND list tombstones (so a new list never reuses a deleted slug, which
        would otherwise be suppressed by the tombstone on merge).
        """
        import re

        slug = re.sub(r"[^a-z0-9]+", "-", base.strip().lower()).strip("-")
        slug = slug or "list"
        taken = set(self.state.lists) | set(self.state.list_tombstones)
        if slug not in taken:
            return slug
        i = 2
        while f"{slug}-{i}" in taken:
            i += 1
        return f"{slug}-{i}"

    @callback
    def async_create_list(
        self, title: str, *, slug: str | None = None
    ) -> ListState:
        """Create a new (empty) list and record an undoable op.

        ``slug`` is derived from the title when not given and always made unique
        against existing lists and list tombstones. The op's ``after`` holds the
        list snapshot so undo can remove it and redo can restore it.
        """
        new_slug = self._unique_slug(slug or title)
        state = ListState(slug=new_slug, title=title or new_slug)
        self.state.lists[new_slug] = state
        self.state.list_tombstones.pop(new_slug, None)
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_LIST,
                scope=new_slug,
                target_id=new_slug,
                before=None,
                after=state.to_dict(),
                label="create_list",
            )
        )
        return state

    @callback
    def async_rename_list(self, slug: str, title: str) -> ListState | None:
        """Rename a list (title only; slug/file stem is stable). Records an op."""
        state = self.state.lists.get(slug)
        if state is None or slug in self.state.list_tombstones:
            return None
        before = state.to_dict()
        state.title = title
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_LIST,
                scope=slug,
                target_id=slug,
                before=before,
                after=state.to_dict(),
                label="rename_list",
            )
        )
        return state

    @callback
    def async_delete_list(self, slug: str) -> bool:
        """Delete a whole list, leaving a list-level tombstone (no resurrect).

        The tombstone is stored centrally (``.grocery/list_tombstones.json``) so
        another device that still has the markdown won't resurrect it on merge.
        The op's ``before`` holds the full list snapshot so undo restores every
        item; its ``after`` is None (deleted).
        """
        state = self.state.lists.get(slug)
        if state is None or slug in self.state.list_tombstones:
            return False
        before = state.to_dict()
        del self.state.lists[slug]
        self.state.list_tombstones[slug] = Tombstone(
            id=slug, deleted_ts=utcnow_iso(), reason="deleted"
        )
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_LIST,
                scope=slug,
                target_id=slug,
                before=before,
                after=None,
                label="delete_list",
            )
        )
        return True

    @callback
    def async_add_item(
        self,
        slug: str,
        name: str,
        *,
        category: str | None = None,
        qty_value: float | None = None,
        qty_unit: str | None = None,
    ) -> Item:
        """Add an item to a list, record the op, and schedule a push."""
        state = self._ensure_list(slug)
        now = utcnow_iso()
        qty = (
            Quantity(value=qty_value, unit=qty_unit or "pcs")
            if qty_value is not None
            else None
        )
        item = Item(
            id=new_id("i-"),
            name=name,
            category=category,
            qty=qty,
            checked=False,
            added_by=self.identity,
            created_ts=now,
            updated_ts=now,
        )
        state.items[item.id] = item
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item.id,
                before=None,
                after=item.to_dict(),
                label="add_item",
            )
        )
        return item

    @callback
    def async_update_item(self, slug: str, item_id: str, **changes) -> Item | None:
        """Apply field changes to an item (name/category/qty), record the op."""
        state = self.state.lists.get(slug)
        if state is None or item_id not in state.items:
            return None
        before = state.items[item_id].to_dict()
        item = state.items[item_id]
        if "name" in changes:
            item.name = changes["name"]
        if "category" in changes:
            item.category = changes["category"]
        if "qty_value" in changes:
            value = changes["qty_value"]
            if value is None:
                item.qty = None
            else:
                unit = changes.get("qty_unit") or (
                    item.qty.unit if item.qty else "pcs"
                )
                item.qty = Quantity(value=value, unit=unit)
        item.updated_ts = utcnow_iso()
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item_id,
                before=before,
                after=item.to_dict(),
                label="update_item",
            )
        )
        return item

    @callback
    def async_set_checked(
        self, slug: str, item_id: str, checked: bool
    ) -> Item | None:
        """Check/uncheck an item (sinks within its category on serialize)."""
        state = self.state.lists.get(slug)
        if state is None or item_id not in state.items:
            return None
        before = state.items[item_id].to_dict()
        item = state.items[item_id]
        item.checked = checked
        now = utcnow_iso()
        item.checked_ts = now if checked else None
        item.updated_ts = now
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item_id,
                before=before,
                after=item.to_dict(),
                label="check_item" if checked else "uncheck_item",
            )
        )
        return item

    @callback
    def async_delete_item(self, slug: str, item_id: str) -> bool:
        """Delete an item, leaving a tombstone so it doesn't resurrect."""
        state = self.state.lists.get(slug)
        if state is None or item_id not in state.items:
            return False
        before = state.items.pop(item_id).to_dict()
        state.tombstones[item_id] = Tombstone(
            id=item_id, deleted_ts=utcnow_iso(), reason="deleted"
        )
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item_id,
                before=before,
                after=None,
                label="delete_item",
            )
        )
        return True

    @callback
    def async_clear_checked(self, slug: str) -> list[str]:
        """Archive+remove all checked items in a list (PLAN §4.6).

        Each cleared item is appended to the per-slug archive (browsable, with
        auto-purge), gets a tombstone with reason ``cleared`` so it can't
        resurrect, and an op so the action is per-identity undoable. Returns the
        cleared item ids.
        """
        state = self.state.lists.get(slug)
        if state is None:
            return []
        cleared: list[str] = []
        now = utcnow_iso()
        archive = self.state.archives.setdefault(slug, [])
        for item_id in [i for i, it in state.items.items() if it.checked]:
            item = state.items.pop(item_id)
            before = item.to_dict()
            archive.append(
                ArchivedItem(item=item, archived_ts=now, reason="cleared")
            )
            state.tombstones[item_id] = Tombstone(
                id=item_id, deleted_ts=now, reason="cleared"
            )
            self.state.oplog.append(
                make_action_op(
                    identity=self.identity,
                    entity=ENTITY_ITEM,
                    scope=slug,
                    target_id=item_id,
                    before=before,
                    after=None,
                    label="clear_checked",
                )
            )
            cleared.append(item_id)
        if cleared:
            self._notify()
            self._schedule_push()
        return cleared

    @callback
    def async_restore_archived(
        self, slug: str, item_id: str, archived_ts: str | None = None
    ) -> Item | None:
        """Restore an archived item back onto its list (PLAN §4.6).

        Undoes a prior clear-checked for a single entry: the archived item is
        re-added to the live list (unchecked so it lands in the active section),
        its ``cleared`` tombstone is dropped so it isn't suppressed on
        serialize/merge, and the matching archive entry is removed. An
        ``add_item``-shaped op is recorded so the restore is itself per-identity
        undoable and syncs like any other change. When ``archived_ts`` is given
        it disambiguates a specific entry (an id can be archived more than once);
        otherwise the newest matching entry is restored. Returns the restored
        item, or ``None`` if no matching archive entry exists.
        """
        archive = self.state.archives.get(slug)
        if not archive:
            return None
        # Pick the target entry: exact (id, archived_ts) if given, else the
        # newest entry for this id (archives are appended in time order).
        idx: int | None = None
        for i in range(len(archive) - 1, -1, -1):
            entry = archive[i]
            if entry.item.id != item_id:
                continue
            if archived_ts is None or entry.archived_ts == archived_ts:
                idx = i
                break
        if idx is None:
            return None
        entry = archive.pop(idx)
        if not archive:
            self.state.archives.pop(slug, None)

        state = self.state.lists.get(slug)
        if state is None:
            state = self._ensure_list(slug)
        item = entry.item
        # Land in the active section and mark as freshly touched by us.
        item.checked = False
        item.checked_ts = None
        item.updated_ts = utcnow_iso()
        state.items[item.id] = item
        # Drop the clear-checked tombstone so serialize/merge keep the item.
        state.tombstones.pop(item.id, None)
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item.id,
                before=None,
                after=item.to_dict(),
                label="restore_archived",
            )
        )
        return item

    @callback
    def async_purge_archives(self) -> int:
        """Drop archived entries older than the retention window (PLAN §4.6).

        Runs deterministically by age so all identities converge without any
        3-way logic: an entry whose ``archived_ts`` is older than
        ``now - retention_days`` is removed and its tombstone reason is upgraded
        to ``purged``. Returns the number of entries purged. Empty per-slug
        lists are pruned from the archives mapping so no empty archive file is
        written. Auto-purge is a local janitorial action and is intentionally
        *not* recorded in the op-log (it is not user-undoable).
        """
        days = self._archive_retention_days
        if days <= 0:
            return 0
        cutoff = _iso_days_ago(days)
        purged = 0
        for slug in list(self.state.archives):
            entries = self.state.archives[slug]
            kept: list[ArchivedItem] = []
            for entry in entries:
                if entry.archived_ts < cutoff:
                    purged += 1
                    state = self.state.lists.get(slug)
                    if state is not None:
                        state.tombstones[entry.item.id] = Tombstone(
                            id=entry.item.id,
                            deleted_ts=utcnow_iso(),
                            reason="purged",
                        )
                else:
                    kept.append(entry)
            if kept:
                self.state.archives[slug] = kept
            else:
                del self.state.archives[slug]
        if purged:
            self._notify()
            self._schedule_push()
        return purged

    # -- category mutations -------------------------------------------------

    @callback
    def async_create_category(
        self,
        name: str,
        *,
        icon: str | None = None,
    ):
        """Create a user-managed category and record an undoable op."""
        cat = self.state.categories.create(name, icon=icon)
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_CATEGORY,
                scope="",
                target_id=cat.id,
                before=None,
                after=cat.to_dict(),
                label="create_category",
            )
        )
        return cat

    @callback
    def async_update_category(
        self,
        cat_id: str,
        *,
        name: str | None = None,
        icon: str | None = None,
        order: int | None = None,
    ):
        """Update a category (name/icon/order) and record an undoable op."""
        existing = self.state.categories.categories.get(cat_id)
        before = existing.to_dict() if existing else None
        cat = self.state.categories.update(
            cat_id, name=name, icon=icon, order=order
        )
        if cat is None:
            return None
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_CATEGORY,
                scope="",
                target_id=cat_id,
                before=before,
                after=cat.to_dict(),
                label="update_category",
            )
        )
        return cat

    @callback
    def async_delete_category(self, cat_id: str) -> bool:
        """Delete a category; items referencing it become uncategorized.

        Reassigning affected items to ``None`` is itself a normal item edit so
        it merges cleanly across devices (PLAN §4.4).
        """
        existing = self.state.categories.categories.get(cat_id)
        if existing is None:
            return False
        before = existing.to_dict()
        self.state.categories.delete(cat_id)

        # Reassign affected items to uncategorized across all lists.
        for slug, lstate in self.state.lists.items():
            for item in lstate.items.values():
                if item.category == cat_id:
                    item.category = None
                    item.updated_ts = utcnow_iso()

        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_CATEGORY,
                scope="",
                target_id=cat_id,
                before=before,
                after=None,
                label="delete_category",
            )
        )
        return True

    @callback
    def async_reorder_categories(self, ordered_ids: list[str]) -> None:
        """Set category order and record an op (whole-order snapshot)."""
        before = {
            "order": self.state.categories.order_ids(),
        }
        self.state.categories.reorder(ordered_ids)
        after = {"order": self.state.categories.order_ids()}
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_CATEGORY,
                scope="",
                target_id="__order__",
                before=before,
                after=after,
                label="reorder_categories",
            )
        )

    # -- undo / redo (per identity, PLAN §6) -------------------------------

    def _apply_snapshot(self, op: Op, snapshot: dict | None) -> None:
        """Apply a before/after entity snapshot to the model.

        ``snapshot`` is the desired resulting entity state (or ``None`` to
        delete). Handles both items (scoped to a list) and categories. Order
        pseudo-ops (target ``__order__``) restore the recorded order list.
        """
        if op.entity == ENTITY_ITEM:
            state = self.state.lists.get(op.scope)
            if state is None:
                state = self._ensure_list(op.scope)
            if snapshot is None:
                # delete
                state.items.pop(op.target_id, None)
                state.tombstones[op.target_id] = Tombstone(
                    id=op.target_id, deleted_ts=utcnow_iso(), reason="deleted"
                )
            else:
                state.items[op.target_id] = Item.from_dict(snapshot)
                state.tombstones.pop(op.target_id, None)
                # If this item was previously archived (e.g. via clear-checked),
                # restoring it must also drop the matching archive entry so the
                # archive view stays in sync after an undo.
                archive = self.state.archives.get(op.scope)
                if archive:
                    kept = [a for a in archive if a.item.id != op.target_id]
                    if len(kept) != len(archive):
                        if kept:
                            self.state.archives[op.scope] = kept
                        else:
                            self.state.archives.pop(op.scope, None)
            return

        if op.entity == ENTITY_LIST:
            slug = op.target_id
            if snapshot is None:
                # delete the whole list, leaving a list-level tombstone.
                self.state.lists.pop(slug, None)
                self.state.list_tombstones[slug] = Tombstone(
                    id=slug, deleted_ts=utcnow_iso(), reason="deleted"
                )
            else:
                # (re)create/restore the list from its snapshot and clear any
                # list-level tombstone so it isn't suppressed on serialize/merge.
                self.state.lists[slug] = ListState.from_dict(snapshot)
                self.state.list_tombstones.pop(slug, None)
            return

        # Category entity.
        if op.target_id == "__order__":
            if snapshot and "order" in snapshot:
                self.state.categories.reorder(snapshot["order"])
            return
        if snapshot is None:
            self.state.categories.delete(op.target_id)
        else:
            from .models import Category

            self.state.categories.categories[op.target_id] = (
                Category.from_dict(snapshot)
            )
            self.state.categories.tombstones.pop(op.target_id, None)

    @callback
    def async_undo(self) -> bool:
        """Undo this identity's most recent action (PLAN §6)."""
        marker = self.state.oplog.make_undo_marker(self.identity)
        if marker is None:
            return False
        # marker.after holds the 'before' snapshot we revert to.
        self._apply_snapshot(marker, marker.after)
        self._record_and_schedule(marker)
        return True

    @callback
    def async_redo(self) -> bool:
        """Redo this identity's most recently undone action (PLAN §6)."""
        marker = self.state.oplog.make_redo_marker(self.identity)
        if marker is None:
            return False
        # marker.after holds the snapshot to re-apply.
        self._apply_snapshot(marker, marker.after)
        self._record_and_schedule(marker)
        return True

    @property
    def can_undo(self) -> bool:
        return self.state.oplog.can_undo(self.identity)

    @property
    def can_redo(self) -> bool:
        return self.state.oplog.can_redo(self.identity)

    # -- snapshot (for the websocket API) ----------------------------------

    @callback
    def snapshot(self, *, locale: str = "en") -> dict[str, Any]:
        """Return a JSON-safe snapshot of the full UI state (PLAN §9).

        This is what the websocket API sends on subscribe and on every change.
        Items are grouped-ready (the card sorts/groups); we include the resolved
        category label map for the requested locale so the UI needn't duplicate
        the en-fallback logic.
        """
        return {
            "identity": self.identity,
            "sync_state": self.sync_state,
            "last_synced_commit": self.last_synced_commit,
            "can_undo": self.can_undo,
            "can_redo": self.can_redo,
            "lists": [
                {
                    "slug": slug,
                    "title": state.title,
                    "items": [
                        it.to_dict() for it in state.items.values()
                    ],
                }
                for slug, state in sorted(self.state.lists.items())
                if slug not in self.state.list_tombstones
            ],
            "categories": [
                c.to_dict() for c in self.state.categories.ordered()
            ],
            "category_labels": self.state.categories.names_map(),
            "archives": {
                slug: [a.to_dict() for a in entries]
                for slug, entries in sorted(self.state.archives.items())
            },
        }


def _as_timedelta(seconds: int):
    from datetime import timedelta

    return timedelta(seconds=seconds)


def _iso_days_ago(days: int) -> str:
    """Return the canonical utc timestamp ``days`` in the past.

    Used as the purge cutoff: archived entries with ``archived_ts`` strictly
    less than this string are past the retention window. Matches the format of
    :func:`models.utcnow_iso` (``YYYY-MM-DDTHH:MM:SSZ``) so plain string
    comparison is chronological.
    """
    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
