"""Constants for the Grocery List integration."""

from __future__ import annotations

DOMAIN = "grocery_list"

# Config entry keys
CONF_IDENTITY = "identity"
CONF_AUTH_METHOD = "auth_method"
CONF_REPO_URL = "repo_url"
CONF_SSH_KEY = "ssh_key"
CONF_SSH_KEY_PATH = "ssh_key_path"
CONF_HTTPS_TOKEN = "https_token"
CONF_BRANCH = "branch"
# Optional relative path inside the repo where list files are stored. Empty
# (default) means the repo root: ``<slug>.md``. A value like ``groceries`` or
# ``home/groceries`` stores lists at ``home/groceries/<slug>.md``.
CONF_LISTS_PATH = "lists_path"
# Whether this instance syncs to a git remote. When False the integration runs
# fully local (no clone, no timers, no push/pull); state is persisted to the
# work_dir as plain files so it survives restarts.
CONF_SYNC_ENABLED = "sync_enabled"

# Auth methods
AUTH_SSH = "ssh"
AUTH_HTTPS = "https"

# Options keys (sync cadence, configurable with sensible defaults)
CONF_PUSH_DEBOUNCE = "push_debounce_seconds"
CONF_PULL_INTERVAL = "pull_interval_seconds"

# Sensible defaults
DEFAULT_PUSH_DEBOUNCE = 60          # commit + push 60s after last change
DEFAULT_PULL_INTERVAL = 300         # pull every 5 minutes
DEFAULT_BRANCH = "main"

# Repo layout (paths within the synced git repo). Only ``lists/*.md`` are
# tracked; there is no sync metadata (tombstones/timestamps/ids) on disk.
LISTS_DIR = "lists"

# Sync states surfaced to the UI
SYNC_SYNCED = "synced"
SYNC_PENDING = "pending"
SYNC_SYNCING = "syncing"
SYNC_OFFLINE = "offline"
SYNC_ERROR = "error"
# Local-only mode (no git remote configured); state persists to disk only.
SYNC_LOCAL = "local"

# Storage
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.state"
# Archive (cleared items) is persisted via an HA Store, entirely out of git.
ARCHIVE_STORAGE_KEY = "grocery_list_archive"

# Frontend (custom Lovelace card) — the built card is shipped inside the
# integration and served as a Lovelace resource so users don't add it manually.
FRONTEND_DIR = "frontend"
FRONTEND_CARD_FILENAME = "grocery-list-card.js"
# URL the card JS is served from. The version query string busts the browser
# cache whenever the integration is upgraded.
FRONTEND_URL_BASE = f"/{DOMAIN}/frontend"
FRONTEND_CARD_URL = f"{FRONTEND_URL_BASE}/{FRONTEND_CARD_FILENAME}"
