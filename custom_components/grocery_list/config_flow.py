"""Config and options flow for the Grocery List integration (PLAN §1, §5, §7).

Setup collects:
- an **instance identity name** (becomes ``added_by`` and scopes undo/redo),
- an **auth method** (SSH or HTTPS),
- the **repository URL** and **branch**,
- credentials: SSH key (pasted or file path) or HTTPS token.

The flow **validates by test-clone**: it clones into a throwaway temp directory
in an executor thread and only creates the config entry if the clone succeeds
(PLAN §1). This guarantees the integration never accepts unusable credentials.

The options flow exposes the configurable sync cadence with sensible defaults
(PLAN §5).
"""

from __future__ import annotations

import tempfile
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    AUTH_HTTPS,
    AUTH_SSH,
    CONF_AUTH_METHOD,
    CONF_BRANCH,
    CONF_HTTPS_TOKEN,
    CONF_IDENTITY,
    CONF_LISTS_PATH,
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
)
from .git_backend import (
    GitAuthError,
    GitBackend,
    GitCloneError,
    GitCredentials,
    validate_url_for_method,
)


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_IDENTITY, default=defaults.get(CONF_IDENTITY, "")
            ): str,
            vol.Required(
                CONF_AUTH_METHOD,
                default=defaults.get(CONF_AUTH_METHOD, AUTH_SSH),
            ): vol.In([AUTH_SSH, AUTH_HTTPS]),
            vol.Required(
                CONF_REPO_URL, default=defaults.get(CONF_REPO_URL, "")
            ): str,
            vol.Required(
                CONF_BRANCH, default=defaults.get(CONF_BRANCH, DEFAULT_BRANCH)
            ): str,
            vol.Optional(
                CONF_LISTS_PATH,
                default=defaults.get(CONF_LISTS_PATH, ""),
            ): str,
            vol.Optional(
                CONF_SSH_KEY, default=defaults.get(CONF_SSH_KEY, "")
            ): TextSelector(
                TextSelectorConfig(
                    multiline=True, type=TextSelectorType.TEXT
                )
            ),
            vol.Optional(
                CONF_SSH_KEY_PATH,
                default=defaults.get(CONF_SSH_KEY_PATH, ""),
            ): str,
            vol.Optional(
                CONF_HTTPS_TOKEN,
                default=defaults.get(CONF_HTTPS_TOKEN, ""),
            ): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
        }
    )


class GroceryListConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial configuration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """First step: choose local-only or git-synced operation.

        Sync is optional (some users just want a local shared list on one HA
        instance). We branch to a lightweight identity-only step for local mode
        or the full repo/credentials step for git mode.
        """
        return self.async_show_menu(
            step_id="user",
            menu_options=["local", "git"],
        )

    async def async_step_local(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure a local-only instance (no git remote)."""
        errors: dict[str, str] = {}
        if user_input is not None:
            identity = user_input[CONF_IDENTITY].strip()
            if not identity:
                errors["base"] = "identity_required"
            else:
                await self.async_set_unique_id(f"local#{identity}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=identity,
                    data={
                        CONF_IDENTITY: identity,
                        CONF_SYNC_ENABLED: False,
                    },
                )
        return self.async_show_form(
            step_id="local",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IDENTITY,
                        default=(user_input or {}).get(CONF_IDENTITY, ""),
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_git(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            method = user_input[CONF_AUTH_METHOD]
            url = user_input[CONF_REPO_URL].strip()
            branch = user_input[CONF_BRANCH].strip() or DEFAULT_BRANCH
            lists_path = (
                user_input.get(CONF_LISTS_PATH) or ""
            ).strip().strip("/")

            if not validate_url_for_method(url, method):
                errors["base"] = "invalid_url"
            else:
                # Preserve the key body verbatim (PEM is newline-sensitive);
                # only trim leading/trailing blank lines/whitespace and
                # normalize CRLF that browsers/textareas may introduce.
                _raw_key = user_input.get(CONF_SSH_KEY) or ""
                _key = _raw_key.replace("\r\n", "\n").strip("\n \t") or None
                creds = GitCredentials(
                    method=method,
                    ssh_key_data=_key,
                    ssh_key_path=(
                        user_input.get(CONF_SSH_KEY_PATH) or ""
                    ).strip()
                    or None,
                    https_token=(
                        user_input.get(CONF_HTTPS_TOKEN) or ""
                    ).strip()
                    or None,
                )
                result = await self._async_validate_clone(url, creds, branch)
                if result is None:
                    await self.async_set_unique_id(f"{url}#{branch}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_IDENTITY],
                        data={
                            CONF_IDENTITY: user_input[CONF_IDENTITY],
                            CONF_SYNC_ENABLED: True,
                            CONF_AUTH_METHOD: method,
                            CONF_REPO_URL: url,
                            CONF_BRANCH: branch,
                            CONF_LISTS_PATH: lists_path,
                            CONF_SSH_KEY: user_input.get(CONF_SSH_KEY, ""),
                            CONF_SSH_KEY_PATH: user_input.get(
                                CONF_SSH_KEY_PATH, ""
                            ),
                            CONF_HTTPS_TOKEN: user_input.get(
                                CONF_HTTPS_TOKEN, ""
                            ),
                        },
                    )
                errors["base"] = result

        return self.async_show_form(
            step_id="git",
            data_schema=_user_schema(user_input),
            errors=errors,
        )

    async def _async_validate_clone(
        self, url: str, creds: GitCredentials, branch: str
    ) -> str | None:
        """Attempt a throwaway clone. Return None on success or an error key."""

        def _do_clone() -> None:
            with tempfile.TemporaryDirectory() as tmp:
                backend = GitBackend(tmp, url, creds, branch)
                backend.clone()

        try:
            await self.hass.async_add_executor_job(_do_clone)
        except GitAuthError:
            return "auth_failed"
        except GitCloneError:
            return "clone_failed"
        except Exception:  # noqa: BLE001
            return "clone_failed"
        return None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> GroceryListOptionsFlow:
        return GroceryListOptionsFlow(config_entry)


class GroceryListOptionsFlow(config_entries.OptionsFlow):
    """Handle sync cadence options plus post-setup credential updates.

    For git-synced entries the form also lets the user rotate credentials
    (SSH key, SSH key file path, or HTTPS token) without deleting and
    re-adding the integration, and shows read-only reminders of the local
    git working directory and the configured lists base path inside the
    repo. Credential edits are written back to ``entry.data`` (not options)
    and the entry is reloaded so the coordinator rebuilds its backend.

    Cadence options (push debounce, pull interval) are stored in
    ``entry.options`` as before.
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    @property
    def _is_git(self) -> bool:
        return bool(self._entry.data.get(CONF_SYNC_ENABLED, True)) and bool(
            self._entry.data.get(CONF_REPO_URL)
        )

    def _git_work_dir(self) -> str:
        """Local working-tree path the coordinator clones into (read-only)."""
        return self.hass.config.path(
            f".storage/{DOMAIN}/{self._entry.entry_id}"
        )

    def _lists_base_path(self) -> str:
        """Human-readable repo-relative lists dir (read-only)."""
        raw = (self._entry.data.get(CONF_LISTS_PATH) or "").strip().strip("/")
        return raw or "(repository root)"

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if not self._is_git:
            return await self._async_step_local_options(user_input)
        return await self._async_step_git_options(user_input)

    async def _async_step_local_options(
        self, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Cadence-only options for local (and any non-git) entries."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        opts = self._entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PUSH_DEBOUNCE,
                    default=opts.get(
                        CONF_PUSH_DEBOUNCE, DEFAULT_PUSH_DEBOUNCE
                    ),
                ): vol.All(int, vol.Range(min=5, max=3600)),
                vol.Required(
                    CONF_PULL_INTERVAL,
                    default=opts.get(
                        CONF_PULL_INTERVAL, DEFAULT_PULL_INTERVAL
                    ),
                ): vol.All(int, vol.Range(min=30, max=86400)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

    async def _async_step_git_options(
        self, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Cadence options + credential rotation for git-synced entries.

        Credential fields default to empty; a blank field means "leave the
        stored value unchanged" so we never force the user to re-paste a key
        just to change the pull interval. Only non-empty submissions are
        written back to ``entry.data``.
        """
        errors: dict[str, str] = {}
        data = self._entry.data
        opts = self._entry.options

        if user_input is not None:
            # Split cadence (-> options) from credentials (-> data).
            new_options = {
                CONF_PUSH_DEBOUNCE: user_input[CONF_PUSH_DEBOUNCE],
                CONF_PULL_INTERVAL: user_input[CONF_PULL_INTERVAL],
            }

            # The auth method may be changed here; fall back to the stored one.
            method = user_input.get(
                CONF_AUTH_METHOD, data.get(CONF_AUTH_METHOD, AUTH_SSH)
            )

            # Normalize submitted credentials; blank => keep existing.
            _raw_key = user_input.get(CONF_SSH_KEY) or ""
            _key = _raw_key.replace("\r\n", "\n").strip("\n \t")
            _key_path = (user_input.get(CONF_SSH_KEY_PATH) or "").strip()
            _token = (user_input.get(CONF_HTTPS_TOKEN) or "").strip()

            new_data = dict(data)
            new_data[CONF_AUTH_METHOD] = method
            if _key:
                new_data[CONF_SSH_KEY] = _key
            if _key_path:
                new_data[CONF_SSH_KEY_PATH] = _key_path
            if _token:
                new_data[CONF_HTTPS_TOKEN] = _token

            # Re-validate by test-clone with the effective credentials so we
            # never persist unusable material (mirrors initial setup). When the
            # user switches auth method, the credentials for the newly-selected
            # method must be present (either just entered or previously stored).
            creds = GitCredentials(
                method=method,
                ssh_key_data=(new_data.get(CONF_SSH_KEY) or "") or None,
                ssh_key_path=(new_data.get(CONF_SSH_KEY_PATH) or "") or None,
                https_token=(new_data.get(CONF_HTTPS_TOKEN) or "") or None,
            )
            url = new_data[CONF_REPO_URL]
            branch = new_data.get(CONF_BRANCH, DEFAULT_BRANCH)
            if not validate_url_for_method(url, method):
                errors["base"] = "invalid_url"
            else:
                result = await self._async_validate_clone(url, creds, branch)
                if result is not None:
                    errors["base"] = result
                else:
                    if new_data != dict(data):
                        self.hass.config_entries.async_update_entry(
                            self._entry, data=new_data
                        )
                    return self.async_create_entry(title="", data=new_options)

        method = data.get(CONF_AUTH_METHOD, AUTH_SSH)
        schema_dict: dict[Any, Any] = {
            vol.Required(
                CONF_PUSH_DEBOUNCE,
                default=opts.get(CONF_PUSH_DEBOUNCE, DEFAULT_PUSH_DEBOUNCE),
            ): vol.All(int, vol.Range(min=5, max=3600)),
            vol.Required(
                CONF_PULL_INTERVAL,
                default=opts.get(CONF_PULL_INTERVAL, DEFAULT_PULL_INTERVAL),
            ): vol.All(int, vol.Range(min=30, max=86400)),
            vol.Required(
                CONF_AUTH_METHOD, default=method
            ): vol.In([AUTH_SSH, AUTH_HTTPS]),
        }
        # Expose all credential fields so the user can switch auth method and
        # supply the matching credential. Blank fields keep the stored value;
        # only the credential(s) for the selected method are used at validation.
        schema_dict[vol.Optional(CONF_SSH_KEY, default="")] = TextSelector(
            TextSelectorConfig(multiline=True, type=TextSelectorType.TEXT)
        )
        schema_dict[vol.Optional(CONF_SSH_KEY_PATH, default="")] = str
        schema_dict[vol.Optional(CONF_HTTPS_TOKEN, default="")] = TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={
                "git_work_dir": self._git_work_dir(),
                "lists_base_path": self._lists_base_path(),
            },
        )

    async def _async_validate_clone(
        self, url: str, creds: GitCredentials, branch: str
    ) -> str | None:
        """Attempt a throwaway clone. Return None on success or an error key."""

        def _do_clone() -> None:
            with tempfile.TemporaryDirectory() as tmp:
                backend = GitBackend(tmp, url, creds, branch)
                backend.clone()

        try:
            await self.hass.async_add_executor_job(_do_clone)
        except GitAuthError:
            return "auth_failed"
        except GitCloneError:
            return "clone_failed"
        except Exception:  # noqa: BLE001
            return "clone_failed"
        return None
