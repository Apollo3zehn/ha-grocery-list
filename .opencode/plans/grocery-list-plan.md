# Grocery List for Home Assistant — Implementation Plan & Design Rationale

> This document is self-contained. It captures **what** we are building, **every
> decision made**, and **why**, so it can be handed to a fresh implementer (human
> or LLM) with no other context.

## 0. Goal (in one paragraph)

Build a **HACS-installable Home Assistant plugin** (hosted on Codeberg) that
manages **multiple grocery shopping lists** stored as **human-readable Markdown
files in a git repository**. It syncs in the background like Obsidian (commit +
push after inactivity; pull on a schedule/at startup), survives HA downtime
(lists remain readable on the git host), groups items by **category** in a
user-defined order, supports **structured quantities/units**, **per-identity
shared undo/redo**, **checked-item archiving**, and provides a **slick,
mobile-first, native-feeling UI**. English + German throughout.

---

## 1. Requirements (from the user, verbatim intent)

- HACS plugin, source on Codeberg.
- Git-based **Markdown** storage; background sync via a git server (Obsidian-like).
- Manage **multiple** grocery lists; add/remove items.
- Items **unchecked by default**; checking sinks the item to the **bottom of its
  own category** (category grouping is primary structure).
- **Undo and redo** — must be **proper**, and **shared across devices**
  (see §6 for the precise, agreed semantics).
- Per-item **category** → items are **auto-grouped**; users never manually sort to
  match store layout.
- Items displayed within their categories.
- **Commit + push ~60 s after inactivity**; **indicate unsynced state** to the user.
- **Automatic conflict resolution** (question raised: "how does Obsidian do it?" —
  answered in §5).
- Markdown format so the list is viewable on the git host when HA is down.
- **Setup**: user provides **SSH url + SSH key** OR **HTTPS url + optional token**;
  plugin **clones locally** and **only accepts config if clone succeeds**.
- **English + German** translations.

### Decisions taken during design (with the user)
1. Checked items sink to **bottom of their category** (not whole list).
2. Categories: **user-managed via a central UI**, **empty at first** (no
   developer-shipped set). Users create/edit/reorder/delete categories in the app;
   category definitions are synced in the repo. en + de labels supported per
   category (user-provided). See §4.4.
3. UI: **developer to recommend** — user is a power user who wants a **slick,
   mobile, native-app-like** experience (adds it to phone splashscreen).
4. **Bundle dulwich** for git — but the architecture must **not become a dead
   end**; prioritize clean, maintainable design over short-term simplicity.
5. Undo/redo: in-memory acceptable, but **prefer persistence**; explore tying it
   to commit history. (Final design: persistent + shared — see §6.)
6. Item metadata: **quantity with structured units**, **added_by**, **category**,
   **timestamp**.
7. **Multiple files** (one per list).
8. Sync cadence **configurable with sensible defaults**; **pull on schedule and on
   HA start** (plus before push).
9. Repo is **ours to own** but must stay **clean** for possible future
   interoperability with other tools.
10. Secrets stored in HA config, but **follow best practices** (see §7).
11. Quantity units must be **structured** (not free text).
12. **added_by = one identity per HA integration instance**, and the user sets a
    **configurable instance name** that becomes that identity.
13. Deletion UX: a **"clear checked" button** that **archives** cleared items to
    keep a record; archive is **browsable in a subview** (rarely needed);
    **auto-purge** archived entries after a **configurable timeframe** (sensible
    default).
14. HACS installs **both** the integration and the card from **one repo**.
15. Undo/redo semantics: **per-identity undo/redo over a shared, synced operation
    log** (Option B — see §6 for full rationale).
16. Design must be **attractive, user-friendly, intuitive**.

---

## 2. Core Architectural Decision — "Git is transport, merge is ours"

**THE most important decision. Read this before writing any sync code.**

**Principle:** Git (via bundled `dulwich` + `paramiko`) is used **only** as a
**transport + history layer**. **All conflict resolution/merging happens in our
own Python code, on the parsed data model — never on raw text.**

### Why (the dead-end we are avoiding)
- `dulwich` is a pure-Python git implementation. Its **clone/fetch/push/commit**
  and blob-reading are solid, but its **textual merge** support is weak compared
  to the native `git` binary.
- Home Assistant runs across many install types (Container, Core, Supervised,
  HAOS) where the **`git` binary may be absent**. Bundling a pure-Python client
  (declared in `manifest.json` `requirements`, pip-installed by HA) works
  everywhere with no system dependency.
- If we depended on git's line-merge machinery, bundling dulwich would eventually
  corner us (the "dead end" the user explicitly forbade).

### The escape hatch that makes bundling dulwich safe
- Every item has a **stable ID** and typed fields. The `.md` file is merely a
  **serialization** of a structured model.
- Conflict resolution is a **semantic 3-way merge on the parsed models**, not text.
- The 3-way **base** is a locally persisted **`last_synced_commit`** whose blobs we
  read back — so we need **no git merge-base algorithm and no textual merge**.
- Therefore dulwich only ever does what it is good at: `clone`, `fetch`, `push`,
  `commit` (including 2-parent merge commits), and **read a blob at a commit**.
- Because the merge logic lives **above** the VCS and is **VCS-agnostic**, we can
  later swap dulwich for the `git` binary or GitPython **without touching merge
  code**. No lock-in, no dead end.

### Runtime note
`dulwich`/`paramiko` are **blocking**; HA is asyncio. **All VCS calls must run in
an executor** (`hass.async_add_executor_job`).

---

## 3. Conflict Resolution — "how does Obsidian do it?" (answered) & our approach

- **Obsidian Git** (community plugin) just runs `git pull/push`; conflicts are
  **real git text conflicts** and can leave conflict markers — **not** true
  auto-resolution.
- **Obsidian Sync** (paid) does block/character merge on its **own server**, not git.

We need **neither**. A grocery list is structured data, so we do better:

**Semantic 3-way merge (base / ours / theirs), field-by-field, keyed by item ID:**
- **Additions**: union by ID (two devices adding different items never conflict).
- **Field edits** (name, qty, unit, category): **last-writer-wins by timestamp**.
- **Checked state**: **"checked wins" tiebreak** (if any side marked it bought,
  it's bought) — models real shopping behavior.
- **Deletions / clears / archiving**: represented as **tombstones** so removed
  items don't resurrect when another device still has them.
- Result is serialized, committed as a **2-parent merge commit**, pushed;
  `last_synced_commit` advances.

This is simpler, more robust, and more correct for this domain than text merge,
and keeps files clean/readable on the host.

---

## 4. Data Model & File Formats

### 4.1 Item (conceptual)
```
Item {
  id: string            # stable, e.g. short random; basis for all merging
  name: string          # human text, e.g. "Tomatoes"
  qty: { value: number, unit: unit_id } | null
  category: category_id # references user-managed categories; may be null/unassigned
  checked: boolean
  added_by: string      # the instance identity name (see §4.5)
  created_ts: ISO-8601 UTC
  checked_ts: ISO-8601 UTC | null
  updated_ts: ISO-8601 UTC   # drives last-writer-wins
}
```

### 4.2 List file — `lists/<slug>.md`
Human-readable prose + hidden HTML-comment metadata (invisible when rendered on
Codeberg). Checked items are placed at the **bottom of their category**.
```markdown
# Rewe

## Vegetables
- [ ] Tomatoes ×2 pcs <!-- id:a1b2 cat:cat-veg by:kitchen-pi qty:2:pcs ts:2026-07-19T20:40:00Z upd:… -->
- [x] Potatoes 1 kg <!-- id:c3d4 cat:cat-veg by:anna qty:1:kg ts:… upd:… checked_ts:… -->

## Dairy
- [ ] Milk 2 L <!-- id:e5f6 cat:cat-dairy by:kitchen-pi qty:2:l ts:… upd:… -->
```
Items with no category are grouped under an implicit **"Uncategorized"** section
(rendered last). "Uncategorized" is not a stored category — it is the UI's label
for items whose `category` is null.

### 4.3 Structured quantity & units — `units.yaml` (developer-maintained)
`qty = { value: number, unit: <unit_id> }`. Unit optional → default `pcs`.
Initial unit set (id → en / de), each translated:
`pcs` pieces/Stück · `g` g/g · `kg` kg/kg · `ml` ml/ml · `l` L/l · `pack`
pack/Packung · `bottle` bottle/Flasche · `can` can/Dose · `bunch` bunch/Bund.
(Units remain developer-maintained; only categories moved to user management.)

### 4.4 Categories — **user-managed via central UI**, synced in repo
**No developer-shipped category set. The system starts with zero categories.**
Users create and manage categories in a **central category-management UI** in the
app. Category definitions are stored in the synced repo so all instances share
them, e.g. `.grocery/categories.json` (or `categories.md` for host-readability):
```
Category {
  id: string            # stable id, generated on creation (e.g. cat-veg)
  order: number         # user-defined ordering (drives display + store flow)
  labels: { en: string, de: string }   # user-provided; en fallback if de empty
  icon: string | null   # optional (mdi icon name)
  updated_ts: ISO-8601 UTC              # for merge (LWW)
}
```
- Managed operations: **create, rename (per-locale labels), reorder, set icon,
  delete**. All are ops in the shared op-log (§6) and merge semantically.
- **Deleting a category** does not delete its items; affected items become
  **uncategorized** (category set to null) via tombstone-aware merge.
- Categories are **synced across devices** through the repo like list data.
- Empty-state UX: first run shows an empty, friendly "create your first category"
  prompt; items can still be added as **uncategorized** before any category exists.

### 4.5 Identity — `added_by`
**One identity per HA integration instance.** The user sets a **configurable
instance name** during setup (e.g. `kitchen-pi`), which becomes `added_by` and
**also scopes undo/redo** (see §6).

### 4.6 Archive — `archive/<slug>.md`
- **"Clear checked"** moves checked items out of the active list into the archive
  (append, timestamped) → keeps a record; active file keeps only active items.
- Browsable via a card **Archive subview** (rarely needed, kept out of main flow).
- **Auto-purge** entries older than a configurable window (**default 90 days**).
- Clearing/purging use **tombstones** so items don't resurrect across devices.

### 4.7 Operation log (for shared undo/redo) — `.grocery/oplog.jsonl`
Append-only, synced in the repo. See §6.

---

## 5. Sync Engine

- **Debounced push:** 60 s after last change (configurable).
- **Pull:** every 5 min + on HA start + before every push (all configurable).
- **Each user action = one commit** with a structured message → clean, auditable
  history.
- **Merge flow:** fetch → if remote advanced beyond `last_synced_commit`, load
  **base** (that commit's blobs), **theirs** (remote head), **ours** (working
  model) → semantic 3-way merge (§3) → serialize → **2-parent merge commit** →
  push → advance `last_synced_commit`.
- **Sync states surfaced to UI:** `synced`, `pending` (local unpushed changes),
  `syncing`, `offline/error`. The card shows a clear badge.

---

## 6. Undo / Redo — Shared, Synced, **Per-Identity** (Agreed Option B)

### The problem & why B
In multi-device editing, "undo" is ambiguous when actions interleave:
- **(A) Global undo** reverts the globally most-recent action regardless of which
  device did it → one device can yank away another's action; feels broken.
- **(B) Per-identity undo** reverts **the acting instance's own** most-recent
  action; redo re-applies it. This matches how mature collaborative tools behave
  (e.g. Google Docs, VS Code Live Share) and is what the user chose.

### Design
- A **single shared operation log** (`.grocery/oplog.jsonl`) is **synced via the
  repo**, so every instance sees the full history of operations (each tagged with
  the `added_by` identity that performed it).
- **Undo/redo is scoped to the acting identity:** an instance's undo targets **its
  own** most-recent not-yet-undone operation; redo re-applies its own most-recent
  undone operation.
- **Undo/redo never rewrite git history.** An undo appends a new **inverse
  operation** (and a new commit); a redo appends a re-apply operation. This keeps
  sync safe and the redo stack durable ("proper redo" that survives restarts and
  syncs across devices).
- **Merge-safe:** because the op-log is append-only and operations carry IDs +
  identity + timestamps, it merges under the same semantic rules as list data;
  redo state is derived per identity from the log, so it is consistent everywhere.
- Concurrency nuance (documented for implementer): undo/redo target selection is
  computed from the **merged** op-log state per identity; inverse ops still pass
  through the semantic merge (e.g. "checked wins"), so outcomes stay deterministic.
- Category-management actions (§4.4) are also ops in this log and are undoable
  under the same per-identity rules.

---

## 7. Security / Secrets — Best Practices

- **Important truth:** HA `.storage` is **not encrypted at rest** by default →
  host access is the real security boundary (must be documented).
- **Recommend a repo-scoped deploy key (SSH)** or **repo-scoped fine-grained token
  (HTTPS)** — Codeberg/Forgejo supports these — rather than account-wide
  credentials (revocable, limited blast radius).
- Support providing the **SSH key by file path** (mounted `600`) so the secret
  need not live in `.storage`; also allow pasted key/token for convenience.
- Store config via the standard HA **config entry** mechanism.

---

## 8. UI / UX — Slick, Mobile-First, Native-Feeling

- **Custom Lovelace card** (TypeScript + **Lit**) talking to the integration over
  the **HA WebSocket API** for real-time, instant-feeling updates.
- **Why a custom card (recommended over HA's built-in Todo UI):** the built-in
  `todo` platform can't express categories, structured units, sink-on-check,
  archive subview, or per-identity undo/redo. A custom card gives full control of
  the desired native-app UX. (A `todo`-entity bridge for voice/companion app is a
  deferred phase-2 nicety, not v1.)
- **Design principles:** attractive, intuitive, mobile-first; large touch targets;
  fast quick-add with a numeric **value + unit** stepper; category color/icon
  chips; smooth **sink-on-check** animation; prominent **sync-status badge**;
  minimal taps for the common "add item" flow; light/dark aware; **add-to-
  homescreen (PWA)** so it behaves like a native app; fully **en/de** localized.
- **Views:**
  - main grouped list per list; list switcher;
  - **Category management UI** (central place to create/rename/reorder/delete
    categories, set icons, provide en/de labels) — starts empty;
  - **Archive subview**;
  - undo/redo controls; **clear-checked** action.

---

## 9. Components & Repo Layout

```
custom_components/grocery_list/       # HA integration (Python)
  __init__.py  manifest.json          # manifest declares dulwich, paramiko
  config_flow.py                      # identity name + auth; validate-by-clone
  coordinator.py                      # debounce push, scheduled/startup pull, sync state
  git_backend.py                      # dulwich/paramiko transport ONLY (executor-wrapped)
  merge.py                            # semantic 3-way merge (pure, VCS-agnostic)
  markdown_io.py                      # model <-> markdown (list + archive)
  models.py                           # Item, List, Quantity, Category, Tombstone, Op
  oplog.py                            # shared op-log read/write + per-identity undo/redo
  categories.py                       # user category CRUD + merge (synced in repo)
  websocket_api.py  services.yaml     # real-time API + HA services
  units.yaml                          # developer-maintained units, en/de
  translations/en.json  translations/de.json
grocery-list-card/                    # custom Lovelace card (TS/Lit)
  src/…  dist/grocery-list-card.js  package.json  tsconfig.json
hacs.json                             # HACS metadata; installs integration + card
tests/                                # pytest: merge, markdown_io, oplog, coordinator
README.md
```
**Synced (owned) repo stays clean** for future interop: `lists/*.md`,
`archive/*.md`, `.grocery/categories.json`, `.grocery/oplog.jsonl`,
`.gitattributes`.

---

## 10. Phased Delivery Plan

1. **Scaffold** — repo layout, `manifest.json` (declare `dulwich`,`paramiko`),
   `hacs.json`, `units.yaml`, i18n stubs, README.
2. **Models + Markdown I/O** — `models.py`, `markdown_io.py` (+ unit tests,
   including round-trip and checked-sinking).
3. **Semantic merge engine** — `merge.py` (+ thorough unit tests: add/add,
   edit/edit LWW, checked-wins, tombstones, category merge).
4. **Git backend** — `git_backend.py` (clone/fetch/push/commit/blob-read, SSH via
   paramiko + HTTPS token, executor-wrapped).
5. **Config flow** — identity name, auth (SSH/HTTPS), **validate by test-clone**,
   accept only on success; best-practice secret handling.
6. **Coordinator** — debounced push, scheduled + startup pull, before-push pull,
   sync-state machine, `last_synced_commit` tracking.
7. **Op-log + undo/redo** — `oplog.py`: shared synced log, per-identity
   undo/redo emitting inverse commits.
8. **Categories** — `categories.py`: user CRUD, ordering, en/de labels, icons,
   synced + merge-safe; empty initial state.
9. **WebSocket API + services** — expose lists, items, categories, actions, sync
   state to the card.
10. **Custom card** — grouped view, add/remove, qty+unit stepper, category chips,
    check/sink animation, undo/redo, clear-checked, sync badge, list switcher.
11. **Category management UI** — central create/rename/reorder/delete/icon view.
12. **Archive subview** — browse archived items (+ auto-purge wiring).
13. **Polish** — design refinement, i18n completeness, docs, HACS validation.

---

## 11. Open / Deferred (not in v1)
- `todo` entity bridge for HA voice/companion app (phase 2).
- Global (non-per-identity) undo mode — explicitly rejected in favor of Option B.
- Developer-shipped default categories — explicitly rejected; categories are
  user-managed and start empty.
