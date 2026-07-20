# Grocery List for Home Assistant

Git-synced, Markdown-backed grocery lists for Home Assistant, with a slick
mobile-first custom Lovelace card.

Keep multiple shopping lists (one file per list) in a plain git repository —
readable and editable anywhere (e.g. in Obsidian) — while Home Assistant handles
category grouping, structured quantities, per-identity shared undo/redo, and
archiving. Conflict resolution is a semantic three-way merge done in Python, so
your lists never end up with git conflict markers: **git is only transport, the
merge is ours.**

## Features

- **Multiple lists**, one Markdown file per list, grouped by category.
- **Checked items sink** to the bottom of their category.
- **Structured quantities** (value + unit; units are maintained by the
  integration in `units.yaml`).
- **User-managed categories** with a single free-text name, created and
  reordered from the card (they start empty — no presets are shipped).
- **Per-identity shared undo/redo** backed by an append-only, synced op-log;
  undo/redo emit new commits and never rewrite history.
- **Archiving**: "clear checked" moves items to a browsable archive with
  automatic age-based purge (default 90 days) and tombstones that prevent
  resurrection on the next sync.
- **Configurable sync**: debounced push (default 60s after the last change),
  scheduled pull (default every 5 minutes), plus a pull on Home Assistant start
  and before every push.
- **English and German** translations.

## How it works

Your lists live in a git repository you control (GitHub, Codeberg, Forgejo, a
self-hosted server, ...). The integration clones it locally, reads and writes
Markdown, and syncs in the background. It uses git purely for transport —
clone, fetch, push, commit, and blob reads — and performs all conflict
resolution as a semantic three-way merge (the base is the last synced commit).
This keeps the data files clean and interoperable with other Markdown tools.

The UI is a custom Lovelace card (TypeScript + Lit) that talks to the
integration over the WebSocket API. The integration ships the built card and
registers it automatically — there is no manual Lovelace resource to add.

## Installation (HACS)

1. Add this repository to HACS as a custom repository (category: Integration).
2. Install **Grocery List**.
3. Restart Home Assistant.
4. Go to **Settings -> Devices & Services -> Add Integration** and search for
   **Grocery List**.

## Configuration

Adding the integration opens a config flow that collects:

- **Identity name** — a name for this Home Assistant instance. It is recorded as
  `added_by` on items and scopes this instance's undo/redo history.
- **Auth method** — SSH or HTTPS.
- **Repository URL** and **branch** (default `main`).
- **Credentials**:
  - **SSH**: paste a private key, or provide a path to a key file mounted into
    the container (recommend `chmod 600`).
  - **HTTPS**: a personal access token.

The flow **validates by test-clone**: it clones the repository in the background
and only creates the entry if the clone succeeds, so unusable credentials are
never accepted.

### Options

After setup, open the integration's options to tune:

- **Push debounce** (seconds, default `60`)
- **Pull interval** (seconds, default `300`)
- **Archive retention** (days, default `90`; `0` disables auto-purge)

### A note on secrets

Home Assistant's `.storage` is **not** encrypted at rest. Prefer a
repository-scoped deploy key or token with the minimum required access. When
using SSH, a mounted key file (permissions `600`) is recommended over pasting
the key.

## Using the card

Add a **Custom: Grocery List Card** to any dashboard. The card provides:

- a list switcher across the top,
- an add bar with a quantity stepper and unit/category selectors,
- tap-to-check (checked items sink within their category) and inline editing,
- a toolbar with undo, redo, sync-now, an archive view, and category management,
- a sync-state badge, and
- a "clear checked" action that archives checked items.

## Repository layout

The synced git repo uses:

```
lists/<slug>.md              # one file per list (human-readable Markdown)
archive/<slug>.md            # archived (cleared) items per list
.grocery/categories.json     # user-managed categories + tombstones
.grocery/tombstones/<slug>.json  # per-list deletion tombstones
```

## Services

The same actions the card performs are exposed as services for automations,
scripts, and voice assistants:

- `grocery_list.add_item`
- `grocery_list.clear_checked`
- `grocery_list.undo`
- `grocery_list.redo`
- `grocery_list.sync`

Each accepts an optional `entry_id` (only needed when more than one list
repository is configured).

## Development

The backend is a standard Home Assistant custom integration under
`custom_components/grocery_list/`. The card source is in `grocery-list-card/`
(TypeScript + Lit, built with Rollup); the build emits the bundled card directly
into the integration's `frontend/` directory so it ships as a single artifact.

```bash
# Backend tests
.venv/bin/python -m pytest tests/ -q

# Build the card (outputs into custom_components/grocery_list/frontend/)
cd grocery-list-card && npm install && npm run build

# Type-check the card
npm run lint
```

### Releasing

Releases are tag-driven; HACS installs from GitHub releases. To cut a release:

```bash
# Tag with a semver version prefixed by `v`, then push the tag.
git tag v0.1.0
git push origin v0.1.0
```

Pushing a `v*` tag triggers the release workflow
(`.github/workflows/release.yml`), which builds the card, stamps
`manifest.json` to the tag version, zips the integration, and publishes a
GitHub release with `grocery_list.zip` attached. HACS downloads that zip (see
`zip_release`/`filename` in `hacs.json`). The `Validate` workflow runs
hassfest and HACS checks on every push and pull request.

## License

MIT — see [LICENSE](LICENSE).
