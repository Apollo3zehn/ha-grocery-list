"""Config and options flow for the Grocery List integration (PLAN §1, §5, §7).

Setup collects:
- an **instance identity name** (becomes ``added_by`` and scopes undo/redo),
- an **auth method** (SSH or HTTPS),
- the **repository URL** and **branch**,
- credentials: SSH key (pasted or file path) or HTTPS token.

The flow **validates by test-clone**: it clones into a throwaway temp directory
in an executor thread and only creates the config entry if the clone succeeds
(PLAN §1). This guarantees the integration never accepts unusable credentials.

The options flow exposes the configurable sync cadence and archive retention
with sensible defaults (PLAN §5, §4.6).
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
    CONF_ARCHIVE_RETENTION,
    CONF_AUTH_METHOD,
    CONF_BRANCH,
    CONF_HTTPS_TOKEN,
    CONF_IDENTITY,
    CONF_PULL_INTERVAL,
    CONF_PUSH_DEBOUNCE,
    CONF_REPO_URL,
    CONF_SSH_KEY,
    CONF_SSH_KEY_PATH,
    DEFAULT_ARCHIVE_RETENTION,
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
        errors: dict[str, str] = {}

        if user_input is not None:
            method = user_input[CONF_AUTH_METHOD]
            url = user_input[CONF_REPO_URL].strip()
            branch = user_input[CONF_BRANCH].strip() or DEFAULT_BRANCH

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
                            CONF_AUTH_METHOD: method,
                            CONF_REPO_URL: url,
                            CONF_BRANCH: branch,
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
            step_id="user",
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
    """Handle sync cadence + retention options (PLAN §5, §4.6)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
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
                vol.Required(
                    CONF_ARCHIVE_RETENTION,
                    default=opts.get(
                        CONF_ARCHIVE_RETENTION, DEFAULT_ARCHIVE_RETENTION
                    ),
                ): vol.All(int, vol.Range(min=1, max=3650)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
