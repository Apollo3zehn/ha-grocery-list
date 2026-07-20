"""Async sync coordinator.

This is the orchestration layer that ties everything together at runtime:

- Holds the in-memory :class:`RepoState` (lists) and the in-memory op-log.
- Owns the :class:`GitBackend` and runs every blocking git call in an executor
  (dulwich/paramiko are synchronous; HA is asyncio).
- Implements the sync cadence:
    * **debounced push** ``push_debounce_seconds`` after the last local change,
    * **scheduled pull** every ``pull_interval_seconds``,
    * **pull on HA start**, and **pull before every push**.
- Runs the sync/merge flow: fetch -> if remote advanced load merge-base +
  theirs + ours -> semantic 3-way merge (``repo_state.merge_repo_states``) ->
  serialize -> 2-parent merge commit -> push -> advance ``last_synced_commit``.
- Tracks and surfaces the **sync state** (synced/pending/syncing/offline/error).
- Persists ``last_synced_commit`` via HA ``Store`` and the archive of cleared
  items via a second ``Store`` (entirely out of git).
- Exposes high-level mutation methods (add/update/check/delete item, list CRUD,
  clear-checked, restore-archived, undo/redo) keyed by item identity
  ``(category, name)``.

There is no sync metadata (tombstones/timestamps/ids) in the persisted data.
Deletions are detected structurally by the 3-way merge against the git
merge-base.
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

from .const import (
    ARCHIVE_STORAGE_KEY,
    CONF_AUTH_METHOD,
    CONF_BRANCH,
    CONF_HTTPS_TOKEN,
    CONF_IDENTITY,
    CONF_PULL_INTERVAL,
    CONF_PUSH_DEBOUNCE,
    CONF_REPO_URL,
    CONF_SSH_KEY,
    CONF_SSH_KEY_PATH,
    CONF_SYNC_ENABLED,
    DEFAULT_BRANCH,
    DEFAULT_PULL_INTERVAL,
    DEFAULT_PUSH_DEBOUNCE,
    DOMAIN,
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
from .models import GroceryList, Item, Quantity, identity_key
from .oplog import (
    ENTITY_ITEM,
    ENTITY_LIST,
    Op,
    OpLog,
    make_action_op,
)
from .repo_state import RepoState, merge_repo_states

_LOGGER = logging.getLogger(__name__)


def _utcnow_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (for archive stamps)."""
    return dt_util.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


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
        # Archive of cleared items, persisted out of git via its own Store.
        self._archive_store: Store = Store(
            hass, 1, f"{DOMAIN}.{entry.entry_id}.archive"
        )
        # Per-slug list of archive entries: {"item": {...}, "archived_ts": iso,
        # "reason": "cleared"}. Newest-last within each list.
        self._archived_items: dict[str, list[dict]] = {}
        self._backend: GitBackend | None = None
        self.state = RepoState()
        # Undo/redo op-log is in-memory only (per-identity, per-runtime).
        self._oplog = OpLog()
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
        """Whether this instance syncs to a git remote (vs local-only)."""
        return self.entry.data.get(CONF_SYNC_ENABLED, True)

    @property
    def _push_debounce(self) -> int:
        return self.entry.options.get(CONF_PUSH_DEBOUNCE, DEFAULT_PUSH_DEBOUNCE)

    @property
    def _pull_interval(self) -> int:
        return self.entry.options.get(CONF_PULL_INTERVAL, DEFAULT_PULL_INTERVAL)

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
        """Clone-or-open the repo, load state, and start timers.

        In local-only mode there is no git remote: we ensure the work dir
        exists, load any previously-persisted state files, and return without a
        backend or sync timers.
        """
        await self._async_load_archive()

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
        except GitAuthError:
            self.sync_state = SYNC_ERROR
            raise
        except GitBackendError:
            self.sync_state = SYNC_OFFLINE
            raise

        await self._async_load_working_state()

        # Pull on HA start, then start the periodic pull timer.
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
            if self._local_write_unsub is not None:
                self._local_write_unsub()
                self._local_write_unsub = None
            await self._async_write_local_state()
            return
        if self.sync_state == SYNC_PENDING:
            await self.async_sync()

    # -- state loading ------------------------------------------------------

    async def _async_load_working_state(self) -> None:
        """Load the working-tree ``lists/`` files into an in-memory RepoState."""

        def _read_all() -> dict[str, bytes]:
            import os

            files: dict[str, bytes] = {}
            base = os.path.join(self._work_dir, "lists")
            if not os.path.isdir(base):
                return files
            for root, _dirs, names in os.walk(base):
                for name in names:
                    full = os.path.join(root, name)
                    rel = os.path.relpath(full, self._work_dir)
                    with open(full, "rb") as fh:
                        files[rel.replace(os.sep, "/")] = fh.read()
            return files

        files = await self.hass.async_add_executor_job(_read_all)
        self.state = RepoState.from_files(files)

    async def _async_load_archive(self) -> None:
        """Load the archive of cleared items from its HA Store."""
        stored = await self._archive_store.async_load()
        self._archived_items = stored or {}

    async def _async_save_archive(self) -> None:
        """Persist the archive of cleared items to its HA Store."""
        await self._archive_store.async_save(self._archived_items)

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
        """(Re)arm a short debounce to persist state to disk (local mode)."""
        if self._local_write_unsub is not None:
            self._local_write_unsub()
        self._local_write_unsub = async_call_later(
            self.hass, 2, self._handle_local_write
        )

    async def _handle_local_write(self, _now) -> None:
        self._local_write_unsub = None
        await self._async_write_local_state()

    async def _async_write_local_state(self) -> None:
        """Serialize the model to the work dir and prune stale files."""
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
            base = os.path.join(self._work_dir, "lists")
            if os.path.isdir(base):
                for root, _dirs, names in os.walk(base):
                    for name in names:
                        full = os.path.normpath(os.path.join(root, name))
                        if full not in wanted:
                            os.remove(full)

        await self.hass.async_add_executor_job(_write)

    # -- the sync flow ------------------------------------------------------

    async def async_sync(self) -> None:
        """Fetch, semantic-merge if remote advanced, commit, and push."""
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
            try:
                return backend.commit(
                    f"grocery: update ({self.identity})",
                    self._author(),
                )
            except Exception as err:  # noqa: BLE001
                if "nothing to commit" in str(err).lower():
                    return None
                raise

        await self.hass.async_add_executor_job(_write_and_commit)

    async def _async_merge_with_remote(self, remote_sha: str) -> None:
        """Load merge-base + theirs blobs, merge with ours, write, merge-commit."""
        backend = self._require_backend()

        # Use the git merge-base of our last-synced commit and the remote as the
        # 3-way ancestor so structural deletions are detected correctly.
        base_commit = await self.hass.async_add_executor_job(
            backend.merge_base, self.last_synced_commit, remote_sha
        )

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
        return [f"lists/{slug}.md" for slug in self.state.lists]

    async def _async_set_last_synced(self, sha: str | None) -> None:
        self.last_synced_commit = sha
        await self._store.async_save(
            {"last_synced_commit": sha, "saved_ts": _utcnow_iso()}
        )

    def _author(self) -> str:
        return f"{self.identity} <grocery@{self.identity}.local>"

    # -- op-log helper ------------------------------------------------------

    def _record_and_schedule(self, op: Op) -> None:
        """Append an op to the shared log and arm a debounced push/write."""
        self._oplog.append(op)
        self._notify()
        if self.sync_enabled:
            self._schedule_push()
        else:
            self._schedule_local_write()

    # -- list/item mutations (called by websocket API) ---------------------

    def _ensure_list(self, slug: str, title: str | None = None) -> GroceryList:
        glist = self.state.lists.get(slug)
        if glist is None:
            glist = GroceryList(slug=slug, title=title or slug)
            self.state.lists[slug] = glist
        return glist

    def _unique_slug(self, base: str) -> str:
        """Return a repo-unique slug derived from ``base`` (title or slug)."""
        import re

        slug = re.sub(r"[^a-z0-9]+", "-", base.strip().lower()).strip("-")
        slug = slug or "list"
        taken = set(self.state.lists)
        if slug not in taken:
            return slug
        i = 2
        while f"{slug}-{i}" in taken:
            i += 1
        return f"{slug}-{i}"

    @callback
    def async_create_list(
        self, title: str, *, slug: str | None = None
    ) -> GroceryList:
        """Create a new (empty) list and record an undoable op."""
        new_slug = self._unique_slug(slug or title)
        glist = GroceryList(slug=new_slug, title=title or new_slug)
        self.state.lists[new_slug] = glist
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_LIST,
                scope=new_slug,
                target_id=new_slug,
                before=None,
                after=glist.to_dict(),
                label="create_list",
            )
        )
        return glist

    @callback
    def async_rename_list(self, slug: str, title: str) -> GroceryList | None:
        """Rename a list (title only; slug/file stem is stable). Records an op."""
        glist = self.state.lists.get(slug)
        if glist is None:
            return None
        before = glist.to_dict()
        glist.title = title
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_LIST,
                scope=slug,
                target_id=slug,
                before=before,
                after=glist.to_dict(),
                label="rename_list",
            )
        )
        return glist

    @callback
    def async_delete_list(self, slug: str) -> bool:
        """Delete a whole list. The merge-base makes the deletion stick."""
        glist = self.state.lists.get(slug)
        if glist is None:
            return False
        before = glist.to_dict()
        del self.state.lists[slug]
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
        glist = self._ensure_list(slug)
        qty = (
            Quantity(value=qty_value, unit=qty_unit or "pcs")
            if qty_value is not None
            else None
        )
        item = Item(name=name, category=category, qty=qty, checked=False)
        # Replace any existing item with the same identity key.
        existing = glist.item_by_key(category, name)
        if existing is not None:
            glist.items.remove(existing)
        glist.items.append(item)
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item.key,
                before=existing.to_dict() if existing else None,
                after=item.to_dict(),
                label="add_item",
            )
        )
        return item

    @callback
    def async_update_item(
        self, slug: str, category: str | None, name: str, **changes
    ) -> Item | None:
        """Apply field changes to an item (name/category/qty), record the op."""
        glist = self.state.lists.get(slug)
        if glist is None:
            return None
        item = glist.item_by_key(category, name)
        if item is None:
            return None
        before = item.to_dict()
        if "new_name" in changes:
            item.name = changes["new_name"]
        if "new_category" in changes:
            item.category = changes["new_category"]
        if "qty_value" in changes:
            value = changes["qty_value"]
            if value is None:
                item.qty = None
            else:
                unit = changes.get("qty_unit") or (
                    item.qty.unit if item.qty else "pcs"
                )
                item.qty = Quantity(value=value, unit=unit)
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item.key,
                before=before,
                after=item.to_dict(),
                label="update_item",
            )
        )
        return item

    @callback
    def async_set_checked(
        self, slug: str, category: str | None, name: str, checked: bool
    ) -> Item | None:
        """Check/uncheck an item (sinks within its category on serialize)."""
        glist = self.state.lists.get(slug)
        if glist is None:
            return None
        item = glist.item_by_key(category, name)
        if item is None:
            return None
        before = item.to_dict()
        item.checked = checked
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item.key,
                before=before,
                after=item.to_dict(),
                label="check_item" if checked else "uncheck_item",
            )
        )
        return item

    @callback
    def async_delete_item(
        self, slug: str, category: str | None, name: str
    ) -> bool:
        """Delete an item. The merge-base makes the deletion stick."""
        glist = self.state.lists.get(slug)
        if glist is None:
            return False
        item = glist.item_by_key(category, name)
        if item is None:
            return False
        before = item.to_dict()
        glist.items.remove(item)
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item.key,
                before=before,
                after=None,
                label="delete_item",
            )
        )
        return True

    @callback
    def async_clear_checked(self, slug: str) -> list[str]:
        """Archive+remove all checked items in a list.

        Each cleared item is appended to the per-slug archive (persisted via the
        archive Store) and an op is recorded so the action is per-identity
        undoable. Returns the cleared item identity keys.
        """
        glist = self.state.lists.get(slug)
        if glist is None:
            return []
        cleared: list[str] = []
        now = _utcnow_iso()
        archive = self._archived_items.setdefault(slug, [])
        for item in [it for it in glist.items if it.checked]:
            before = item.to_dict()
            glist.items.remove(item)
            archive.append(
                {"item": before, "archived_ts": now, "reason": "cleared"}
            )
            self._oplog.append(
                make_action_op(
                    identity=self.identity,
                    entity=ENTITY_ITEM,
                    scope=slug,
                    target_id=item.key,
                    before=before,
                    after=None,
                    label="clear_checked",
                )
            )
            cleared.append(item.key)
        if cleared:
            self.hass.async_create_task(self._async_save_archive())
            self._notify()
            if self.sync_enabled:
                self._schedule_push()
            else:
                self._schedule_local_write()
        return cleared

    @callback
    def async_restore_archived(
        self, slug: str, category: str | None, name: str
    ) -> Item | None:
        """Restore an archived item back onto its list.

        The newest matching archive entry for ``(category, name)`` is removed
        and the item re-added to the live list (unchecked). Returns the restored
        item, or ``None`` if no matching archive entry exists.
        """
        archive = self._archived_items.get(slug)
        if not archive:
            return None
        target = identity_key(category, name)
        idx: int | None = None
        for i in range(len(archive) - 1, -1, -1):
            entry_item = archive[i].get("item", {})
            ekey = identity_key(entry_item.get("category"), entry_item.get("name"))
            if ekey == target:
                idx = i
                break
        if idx is None:
            return None
        entry = archive.pop(idx)
        if not archive:
            self._archived_items.pop(slug, None)
        self.hass.async_create_task(self._async_save_archive())

        glist = self._ensure_list(slug)
        item = Item.from_dict(entry["item"])
        item.checked = False
        # Replace any existing item with the same identity key.
        existing = glist.item_by_key(item.category, item.name)
        if existing is not None:
            glist.items.remove(existing)
        glist.items.append(item)
        self._record_and_schedule(
            make_action_op(
                identity=self.identity,
                entity=ENTITY_ITEM,
                scope=slug,
                target_id=item.key,
                before=None,
                after=item.to_dict(),
                label="restore_archived",
            )
        )
        return item

    # -- undo / redo (per identity) ----------------------------------------

    def _apply_snapshot(self, op: Op, snapshot: dict | None) -> None:
        """Apply a before/after entity snapshot to the model.

        ``snapshot`` is the desired resulting entity state (or ``None`` to
        delete). Handles items (scoped to a list, keyed by identity) and whole
        lists.
        """
        if op.entity == ENTITY_ITEM:
            glist = self.state.lists.get(op.scope)
            if glist is None:
                glist = self._ensure_list(op.scope)
            # Remove any current item matching the op's target identity key.
            for existing in list(glist.items):
                if existing.key == op.target_id:
                    glist.items.remove(existing)
            if snapshot is not None:
                glist.items.append(Item.from_dict(snapshot))
            return

        if op.entity == ENTITY_LIST:
            slug = op.target_id
            if snapshot is None:
                self.state.lists.pop(slug, None)
            else:
                self.state.lists[slug] = GroceryList.from_dict(snapshot)
            return

    @callback
    def async_undo(self) -> bool:
        """Undo this identity's most recent action."""
        marker = self._oplog.make_undo_marker(self.identity)
        if marker is None:
            return False
        self._apply_snapshot(marker, marker.after)
        self._record_and_schedule(marker)
        return True

    @callback
    def async_redo(self) -> bool:
        """Redo this identity's most recently undone action."""
        marker = self._oplog.make_redo_marker(self.identity)
        if marker is None:
            return False
        self._apply_snapshot(marker, marker.after)
        self._record_and_schedule(marker)
        return True

    @property
    def can_undo(self) -> bool:
        return self._oplog.can_undo(self.identity)

    @property
    def can_redo(self) -> bool:
        return self._oplog.can_redo(self.identity)

    # -- snapshot (for the websocket API) ----------------------------------

    @callback
    def snapshot(self, *, locale: str = "en") -> dict[str, Any]:
        """Return a JSON-safe snapshot of the full UI state."""
        return {
            "identity": self.identity,
            "sync_state": self.sync_state,
            "last_synced_commit": self.last_synced_commit,
            "can_undo": self.can_undo,
            "can_redo": self.can_redo,
            "lists": [
                {
                    "slug": slug,
                    "title": glist.title,
                    "items": [it.to_dict() for it in glist.items],
                }
                for slug, glist in sorted(self.state.lists.items())
            ],
            "categories": sorted(
                {
                    it.category
                    for glist in self.state.lists.values()
                    for it in glist.items
                    if it.category
                }
            ),
            "archives": {
                slug: list(entries)
                for slug, entries in sorted(self._archived_items.items())
            },
        }


def _as_timedelta(seconds: int):
    from datetime import timedelta

    return timedelta(seconds=seconds)
