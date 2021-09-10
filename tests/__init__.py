"""Tests for myenergi integration."""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

from custom_components.myenergi import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG

TEST_CONFIG_ENTRY_ID = "77889900ab"


def load_fixture_json(name):
    with open(f"tests/fixtures/{name}.json") as json_file:
        data = json.load(json_file)
        return data


def create_mock_myenergi_config_entry(
    hass: HomeAssistant,
    data: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> ConfigEntry:
    """Add a test config entry."""
    config_entry: MockConfigEntry = MockConfigEntry(
        entry_id=TEST_CONFIG_ENTRY_ID,
        domain=DOMAIN,
        data=data or MOCK_CONFIG,
        title="",
        options=options or {},
    )
    config_entry.add_to_hass(hass)
    return config_entry


async def setup_mock_myenergi_config_entry(
    hass: HomeAssistant,
    data: dict[str, Any] | None = None,
    config_entry: ConfigEntry | None = None,
    client: Mock | None = None,
) -> ConfigEntry:
    """Add a mock sunspec config entry to hass."""
    config_entry = config_entry or create_mock_myenergi_config_entry(hass, data)
    """Mock data from client.fetch_data()"""
    with patch(
        "pymyenergi.client.MyenergiClient.fetch_data",
        return_value=load_fixture_json("client"),
    ), patch(
        "pymyenergi.zappi.Zappi.fetch_history_data",
        return_value=load_fixture_json("history_zappi"),
    ), patch(
        "pymyenergi.eddi.Eddi.fetch_history_data",
        return_value=load_fixture_json("history_eddi"),
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
    return config_entry
