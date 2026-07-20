# Grocery List: Remove Sync Metadata, Use Git Merge-Base for Deletions

## Goal

Rewrite the grocery list integration to remove all sync metadata (tombstones,
timestamps, IDs) from the persisted data model. Use git's merge base
(`last_synced_commit`) as the 3-way merge ancestor to distinguish "deleted"
from "never-seen" items. Keep the archive feature but persist it in an HA
`Store` instead of git.

## Design Constraints & Preferences

- Remove all tombstones, timestamps, and IDs from the `Item` model.
- Item identity = `(category, name)`. No persisted IDs needed.
- Keep archive feature but persist in HA `Store` (handled internally by HA),
  not in git.
- Clean markdown format with no HTML comments or metadata on disk.
- 3-way merge at item level keyed by `(category, name)`; `checked` uses
  checked-wins.
- No git binary dependencies — pure Python via dulwich.
- `.grocery/` directory, `TOMBSTONE_FILE`, `LIST_TOMBSTONE_FILE`, `ARCHIVE_DIR`
  all removed. Tracked paths = only `lists/*.md`.

## Key Design Decisions

- **Item identity** = `(category, name)`; the merge key string is
  `f"{category or ''}|{name}"`.
- **Delete vs edit**: git merge-base is the ancestor. If an item is absent on
  one side but present in base, it was deleted; the merge honors that. Presence
  on a side not in base = addition (unioned in).
- **Quantity conflict**: last-writer-wins via base-relative 3-way; when both
  sides changed and no ancestor distinguishes, prefer a deterministic winner.
- **Checked conflict**: checked-wins (if either side checked, result checked).
- **Archive** moved to HA `Store` (key `grocery_list_archive` /
  `{DOMAIN}.{entry_id}.archive`) as JSON, entirely out of git.
- **Undo/redo** remains in-memory only (was already removed from git in commit
  `350e981`).

## Files & Required Changes

### `const.py`
- Remove `ARCHIVE_DIR`, `META_DIR`, `LIST_TOMBSTONES_FILE`, `TOMBSTONES_DIR`,
  `CONF_ARCHIVE_RETENTION`, `DEFAULT_ARCHIVE_RETENTION`.
- Keep `LISTS_DIR = "lists"`. Only `lists/*.md` are tracked.
- Add `ARCHIVE_STORAGE_KEY = "grocery_list_archive"`.
- Keep sync-state constants, storage constants, frontend constants unchanged.

### `models.py`
Shrink to just `Quantity`, `Item`, `GroceryList`:
- `Item`: fields `name: str`, `category: str | None = None`,
  `qty: Quantity | None = None`, `checked: bool = False`. `to_dict`/`from_dict`
  only serialize these four. Keep `copy(**changes)` via `dataclasses.replace`.
- Remove `Tombstone`, `ArchivedItem`, `ListState`, `new_id`, `utcnow_iso`
  (drop `secrets`; `utcnow_iso` only if nothing else needs it — coordinator now
  uses `dt_util`).
- `GroceryList`: `slug`, `title`, `items: list[Item]`. Remove `item_by_id`.
  Keep `to_dict`/`from_dict`.
- Optional helper: `identity_key(category, name)` returning
  `f"{category or ''}|{name}"`.

### `markdown_io.py`
Clean, metadata-free format:
- `serialize(glist, uncategorized_label="Uncategorized")`:
  - `# <title>` heading, blank line.
  - Bucket items by `category` (None -> `""` sentinel).
  - Section order: category names alphabetically, uncategorized last.
  - `## <label>` per section; within a section sort by
    `(checked, name.lower())` so checked sink to bottom.
  - Item line: `- [ ] Name` or `- [x] Name`, with optional
    ` ×<value> <unit>` quantity suffix (integers rendered without `.0`).
- `parse(text)`:
  - `# ` -> title; `## ` -> resets current category to None (per-item category
    is derived from section only in the fallback; see note below).
  - `- [ ]` / `- [x]` -> item; parse optional ` ×VALUE UNIT` suffix into
    `Quantity`.
  - Derive slug from slugified title.
- Remove `serialize_archive` / `parse_archive` and all HTML-comment metadata
  helpers (`_encode_meta`, `_parse_meta`, etc.).
- **Note/limitation to resolve during implementation**: the current draft
  `parse` sets `current_category = None` on every `## ` header, so parsed items
  lose their category. This must be fixed to capture the header label
  (mapping the uncategorized label back to `None`) so round-trip is lossless.

### `merge.py`
~40 lines, operate on `GroceryList` keyed by `(category, name)`:
- `key(item) = f"{item.category or ''}|{item.name}"`.
- `merge(base, ours, theirs) -> GroceryList`:
  - Union of keys across the three sides.
  - Both sides present -> `_merge_item_fields` (checked = ours or theirs;
    field winner deterministic — quantity/name/category).
  - Present on exactly one side and NOT in base -> addition, keep it.
  - Present in base but missing on a side -> deletion; honor it (drop).
  - Title: last-writer-wins-ish (prefer the side that changed vs base;
    tie -> ours).
- **Note to resolve**: the current draft ignores `base` for deletions (keeps an
  item present on either side). Correct implementation must use `base` to
  distinguish deletion (in base, gone one side) from addition (not in base).

### `repo_state.py`
- `RepoState` holds only `lists: dict[str, GroceryList]`.
- Remove `archives`, `list_tombstones`, all tombstone/archive path regexes and
  helpers. Keep `_SLUG_FROM_PATH` for `lists/<slug>.md`.
- `from_files`: parse only `lists/*.md`; set `glist.slug` from filename.
- `to_files`: serialize each list to `lists/<slug>.md`.
- `merge_repo_states(base, ours, theirs)`: union slugs; per slug call
  `merge.merge` with empty `GroceryList(slug, title=slug)` for missing sides.

### `coordinator.py`
- Drop imports of `ArchivedItem`, `ListState`, `Tombstone`, `new_id`,
  `utcnow_iso`, `LIST_TOMBSTONES_FILE`, archive-retention consts. Use
  `GroceryList`, `Item`, `Quantity` and `dt_util` for timestamps.
- Add a second `Store` for the archive:
  `self._archive_store = Store(hass, 1, f"{DOMAIN}.{entry_id}.archive")`, and an
  in-memory `self._archived_items: dict[str, list[dict]]` loaded in
  `_async_load_working_state` (`await self._archive_store.async_load() or {}`).
- `_async_load_working_state`: read only the `lists/` subtree (drop
  `.grocery`/`archive`).
- `_async_write_local_state`: write only `lists/`; persist archive JSON via the
  archive store (or work-dir file in local mode).
- `_tracked_paths`: return only `[f"lists/{slug}.md" for slug in state.lists]`.
- Mutations rewritten to key by `(category, name)` instead of item id:
  - `_ensure_list` returns a `GroceryList`; items are a `list[Item]`.
  - `async_add_item`: append `Item(name, category, qty, checked=False)`.
  - `async_update_item(slug, category, name, **changes)`: find by key, apply
    `name`/`category`/`qty_value`(+`qty_unit`)/`checked`.
  - `async_set_checked(slug, category, name, checked)`: find by key, set flag.
  - `async_delete_item(slug, category, name)`: remove by key (no tombstone).
  - `async_clear_checked(slug)`: move checked items into `_archived_items[slug]`
    (store dict `{item, archived_ts, reason:"cleared"}`) and remove from list.
  - `async_restore_archived(slug, category, name)`: pop matching archive entry,
    re-add `Item` (checked=False) to the list.
  - `async_purge_archives`: no-op returning 0 (retention removed) — or drop
    entirely and remove callers.
- `_apply_snapshot` (undo/redo): items keyed by `(category, name)`; snapshot
  None -> remove by key; else append `Item.from_dict`. Lists: None -> pop;
  else `GroceryList.from_dict`.
- `snapshot()`: lists render `items` from `state.items` (a list); `categories`
  derived from item categories; `archives` = `self._archived_items`. Remove all
  `list_tombstones` filtering.
- Op-log calls: `target_id` becomes the `(category, name)` key string.

### Tests
- `tests/__init__.py`, `tests/conftest.py` exist (currently stubbed — restore
  real content / fixtures as needed; ensure `custom_components` is importable as
  `grocery_list`).
- `tests/test_repo_state.py`: rewritten to new API — covers empty state,
  serialization (`lists/test.md` contains `# Test List`), merge add-list,
  title-conflict ours-wins, checked-wins, delete-vs-edit, name-change.
- `tests/test_markdown_io.py`, `tests/test_coordinator.py`, `tests/test_oplog.py`
  must be updated to the new models (no `id`/timestamps; key by
  `(category, name)`).

## Important Recovery Note

Before this plan was written, 8 source files under
`custom_components/grocery_list/` (`__init__.py`, `const.py`, `coordinator.py`,
`git_backend.py`, `markdown_io.py`, `merge.py`, `models.py`, `repo_state.py`,
`services.py`) plus `tests/__init__.py`, `tests/conftest.py`,
`tests/test_repo_state.py` were accidentally overwritten with a one-line stub
(`"""Tests for the Grocery List integration."""`). The user will restore these
from git (`git restore <file>` / checkout `HEAD`) before applying this plan.
The intended (pre-stub) rewrites for `const.py`, `models.py`, `markdown_io.py`,
`merge.py`, `repo_state.py`, `coordinator.py`, and `tests/test_repo_state.py`
are described in full above and should be re-applied on top of the restored
files.

## Current Repo State (at planning time)

- Branch `main`, ahead of `origin/main` by 1 commit.
- Working tree has the accidental stub changes (unstaged). User will discard.
- Real module set: `markdown_io.py` (not `markdown.py`), `websocket_api.py`
  (not `websocket.py`), plus `oplog.py`, `units.py`, `repo_state.py`,
  `git_backend.py`, `services.py`, `frontend.py`, `config_flow.py`.
- `git_backend.py` uses dulwich (no git binary). Do not add git-binary deps.

## Suggested Implementation Order

1. Restore all stubbed files from git (user does this).
2. `const.py` -> `models.py` -> `markdown_io.py` -> `merge.py` ->
   `repo_state.py` -> `coordinator.py`.
3. Fix the two correctness notes (markdown category round-trip; merge base-aware
   deletion).
4. Update `websocket_api.py` handlers to the `(category, name)` mutation
   signatures.
5. Update tests; run the suite until green.
