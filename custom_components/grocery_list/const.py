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

# Auth methods
AUTH_SSH = "ssh"
AUTH_HTTPS = "https"

# Options keys (sync cadence, configurable with sensible defaults)
CONF_PUSH_DEBOUNCE = "push_debounce_seconds"
CONF_PULL_INTERVAL = "pull_interval_seconds"
CONF_ARCHIVE_RETENTION = "archive_retention_days"

# Sensible defaults
DEFAULT_PUSH_DEBOUNCE = 60          # commit + push 60s after last change
DEFAULT_PULL_INTERVAL = 300         # pull every 5 minutes
DEFAULT_ARCHIVE_RETENTION = 90      # auto-purge archived items after 90 days
DEFAULT_BRANCH = "main"

# Repo layout (paths within the synced git repo)
LISTS_DIR = "lists"
ARCHIVE_DIR = "archive"
META_DIR = ".grocery"
CATEGORIES_FILE = f"{META_DIR}/categories.json"
OPLOG_FILE = f"{META_DIR}/oplog.jsonl"
# Central registry of list-level tombstones (deleted lists) so a delete on one
# device isn't resurrected by another that still has the list markdown. Mirrors
# the category tombstone pattern; list *existence*/title live in the markdown.
LIST_TOMBSTONES_FILE = f"{META_DIR}/list_tombstones.json"
# Per-list tombstones live outside the human-readable markdown so list files
# stay clean on the git host; they are recombined into ListState for merging.
TOMBSTONES_DIR = f"{META_DIR}/tombstones"

# Sync states surfaced to the UI
SYNC_SYNCED = "synced"
SYNC_PENDING = "pending"
SYNC_SYNCING = "syncing"
SYNC_OFFLINE = "offline"
SYNC_ERROR = "error"

# Storage
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.state"

# Frontend (custom Lovelace card) — the built card is shipped inside the
# integration and served as a Lovelace resource so users don't add it manually.
FRONTEND_DIR = "frontend"
FRONTEND_CARD_FILENAME = "grocery-list-card.js"
# URL the card JS is served from. The version query string busts the browser
# cache whenever the integration is upgraded.
FRONTEND_URL_BASE = f"/{DOMAIN}/frontend"
FRONTEND_CARD_URL = f"{FRONTEND_URL_BASE}/{FRONTEND_CARD_FILENAME}"
