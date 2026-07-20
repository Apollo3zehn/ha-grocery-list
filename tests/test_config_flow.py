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

from custom_components.grocery_list.const import (
    AUTH_HTTPS,
    CONF_AUTH_METHOD,
    CONF_BRANCH,
    CONF_IDENTITY,
    CONF_REPO_URL,
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
    for comp in ("http", "websocket_api", "frontend"):
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
