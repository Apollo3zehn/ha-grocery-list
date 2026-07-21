"""Tests for the Grocery List config flow (PLAN §8).

Covers the menu-based first step (local vs git) and the local-only path end to
end. The git path's clone validation is exercised indirectly by mocking the
clone probe so no network/SSH is required.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.grocery_list.const import (
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
    DOMAIN,
)


@pytest.fixture(autouse=True)
def _enable_custom_integrations(enable_custom_integrations):
    """Make the grocery_list custom integration discoverable in the flow."""
    yield


@pytest.fixture(autouse=True)
def _stub_dependencies(hass: HomeAssistant):
    """Pretend heavy runtime deps are already set up.

    Creating a config entry triggers entry setup, which would otherwise set up
    the ``frontend`` component and fail (``hass_frontend`` isn't installed in
    the test env). Marking the deps as already-loaded lets the flow complete;
    the flow itself needs none of them.
    """
    for comp in ("http", "websocket_api", "frontend", "lovelace"):
        hass.config.components.add(comp)
    yield


async def test_user_step_shows_menu(hass: HomeAssistant):
    """The first step is a menu offering local vs git."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.MENU
    assert set(result["menu_options"]) == {"local", "git"}


async def test_local_flow_creates_entry(hass: HomeAssistant):
    """The local path collects only an identity and creates a local entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "local"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "local"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_IDENTITY: "kitchen-pi"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_IDENTITY: "kitchen-pi",
        CONF_SYNC_ENABLED: False,
    }


async def test_local_flow_requires_identity(hass: HomeAssistant):
    """An empty identity is rejected in the local path."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "local"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_IDENTITY: "   "}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "identity_required"}


async def test_git_flow_creates_entry_on_successful_clone(hass: HomeAssistant):
    """The git path validates by cloning and stores sync_enabled=True."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "git"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "git"

    with patch(
        "custom_components.grocery_list.config_flow.GroceryListConfigFlow."
        "_async_validate_clone",
        return_value=None,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IDENTITY: "kitchen-pi",
                CONF_AUTH_METHOD: AUTH_HTTPS,
                CONF_REPO_URL: "https://example.com/x/y.git",
                CONF_BRANCH: "main",
            },
        )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_SYNC_ENABLED] is True
    assert result["data"][CONF_REPO_URL] == "https://example.com/x/y.git"


async def test_git_flow_clone_failure_shows_error(hass: HomeAssistant):
    """A failed clone surfaces an error instead of creating an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "git"}
    )
    with patch(
        "custom_components.grocery_list.config_flow.GroceryListConfigFlow."
        "_async_validate_clone",
        return_value="clone_failed",
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IDENTITY: "kitchen-pi",
                CONF_AUTH_METHOD: AUTH_HTTPS,
                CONF_REPO_URL: "https://example.com/x/y.git",
                CONF_BRANCH: "main",
            },
        )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "clone_failed"}


# ---------------------------------------------------------------------------
# Options flow
# ---------------------------------------------------------------------------


def _make_git_entry(
    hass: HomeAssistant, overrides: dict | None = None
) -> MockConfigEntry:
    """Create and register a git-synced config entry for options tests."""
    data = {
        CONF_IDENTITY: "kitchen-pi",
        CONF_SYNC_ENABLED: True,
        CONF_AUTH_METHOD: AUTH_SSH,
        CONF_REPO_URL: "ssh://git@example.com/x/y.git",
        CONF_BRANCH: "main",
        CONF_LISTS_PATH: "path/to/lists",
        CONF_SSH_KEY: "OLD_KEY",
        CONF_SSH_KEY_PATH: "",
        CONF_HTTPS_TOKEN: "",
    }
    data.update(overrides or {})
    entry = MockConfigEntry(domain=DOMAIN, data=data, options={})
    entry.add_to_hass(hass)
    return entry


async def test_options_local_entry_shows_cadence_only(hass: HomeAssistant):
    """A local-only entry gets just the cadence options (no credentials)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_IDENTITY: "kitchen-pi", CONF_SYNC_ENABLED: False},
        options={},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "init"
    schema_keys = {str(k.schema) for k in result["data_schema"].schema}
    assert CONF_PUSH_DEBOUNCE in schema_keys
    assert CONF_PULL_INTERVAL in schema_keys
    assert CONF_SSH_KEY not in schema_keys
    assert CONF_HTTPS_TOKEN not in schema_keys

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_PUSH_DEBOUNCE: 30, CONF_PULL_INTERVAL: 120},
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_PUSH_DEBOUNCE: 30,
        CONF_PULL_INTERVAL: 120,
    }


async def test_options_git_entry_shows_ssh_fields_and_placeholders(
    hass: HomeAssistant,
):
    """A git+SSH entry exposes SSH credential fields and readonly paths."""
    entry = _make_git_entry(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    schema_keys = {str(k.schema) for k in result["data_schema"].schema}
    assert CONF_SSH_KEY in schema_keys
    assert CONF_SSH_KEY_PATH in schema_keys
    assert CONF_HTTPS_TOKEN not in schema_keys
    placeholders = result["description_placeholders"]
    assert entry.entry_id in placeholders["git_work_dir"]
    assert placeholders["lists_base_path"] == "path/to/lists"


async def test_options_git_entry_https_shows_token_field(hass: HomeAssistant):
    """A git+HTTPS entry exposes the token field and repo-root placeholder."""
    entry = _make_git_entry(
        hass,
        {
            CONF_AUTH_METHOD: AUTH_HTTPS,
            CONF_REPO_URL: "https://example.com/x/y.git",
            CONF_LISTS_PATH: "",
            CONF_SSH_KEY: "",
            CONF_HTTPS_TOKEN: "OLD_TOKEN",
        },
    )

    result = await hass.config_entries.options.async_init(entry.entry_id)
    schema_keys = {str(k.schema) for k in result["data_schema"].schema}
    assert CONF_HTTPS_TOKEN in schema_keys
    assert CONF_SSH_KEY not in schema_keys
    assert (
        result["description_placeholders"]["lists_base_path"]
        == "(repository root)"
    )


async def test_options_git_blank_credentials_keep_existing(
    hass: HomeAssistant,
):
    """Submitting blank credential fields leaves stored values unchanged."""
    entry = _make_git_entry(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    with patch(
        "custom_components.grocery_list.config_flow."
        "GroceryListOptionsFlow._async_validate_clone",
        return_value=None,
    ):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {
                CONF_PUSH_DEBOUNCE: 45,
                CONF_PULL_INTERVAL: 200,
                CONF_SSH_KEY: "",
                CONF_SSH_KEY_PATH: "",
            },
        )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    # Cadence saved to options.
    assert result["data"] == {
        CONF_PUSH_DEBOUNCE: 45,
        CONF_PULL_INTERVAL: 200,
    }
    # Stored key unchanged.
    assert entry.data[CONF_SSH_KEY] == "OLD_KEY"


async def test_options_git_updates_ssh_key(hass: HomeAssistant):
    """A new SSH key is validated and written back to entry.data."""
    entry = _make_git_entry(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    with patch(
        "custom_components.grocery_list.config_flow."
        "GroceryListOptionsFlow._async_validate_clone",
        return_value=None,
    ) as mock_validate:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {
                CONF_PUSH_DEBOUNCE: 60,
                CONF_PULL_INTERVAL: 300,
                CONF_SSH_KEY: "NEW_KEY",
                CONF_SSH_KEY_PATH: "",
            },
        )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert mock_validate.called
    assert entry.data[CONF_SSH_KEY] == "NEW_KEY"


async def test_options_git_invalid_credentials_show_error(
    hass: HomeAssistant,
):
    """A failed re-validation surfaces an error and does not persist."""
    entry = _make_git_entry(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    with patch(
        "custom_components.grocery_list.config_flow."
        "GroceryListOptionsFlow._async_validate_clone",
        return_value="auth_failed",
    ):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {
                CONF_PUSH_DEBOUNCE: 60,
                CONF_PULL_INTERVAL: 300,
                CONF_SSH_KEY: "BAD_KEY",
                CONF_SSH_KEY_PATH: "",
            },
        )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "auth_failed"}
    # Unchanged.
    assert entry.data[CONF_SSH_KEY] == "OLD_KEY"
