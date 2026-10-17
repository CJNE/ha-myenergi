"""Test myenergi sensor."""

import copy
from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import MagicMock
from unittest.mock import patch

from custom_components.myenergi.const import DOMAIN

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_OPTION
from homeassistant.const import SERVICE_SELECT_OPTION
from homeassistant.core import HomeAssistant

from . import load_fixture_json
from . import setup_mock_myenergi_config_entry

TEST_ZAPPI_SELECT_CHARGE_MODE = "select.myenergi_test_zappi_1_charge_mode"
TEST_ZAPPI_SELECT_PHASE_SETTING = "select.myenergi_test_zappi_1_phase_setting"
TEST_EDDI_SELECT_OP_MODE = "select.myenergi_test_eddi_1_operating_mode"


async def test_zappi_select(
    hass: HomeAssistant, mock_zappi_set_phase_setting: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_zappi_set_phase_setting.call_count == 0
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_PHASE_SETTING,
            ATTR_OPTION: "1",
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_zappi_set_phase_setting.call_count == 1
    mock_zappi_set_phase_setting.assert_called_with("1")


async def test_zappi_phaseselect(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_zappi_set_charge_mode.call_count == 0
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
            ATTR_OPTION: "Eco+",
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_zappi_set_charge_mode.call_count == 1
    mock_zappi_set_charge_mode.assert_called_with("Eco+")


async def test_eddi_select(
    hass: HomeAssistant, mock_eddi_set_operating_mode: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_eddi_set_operating_mode.call_count == 0
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: TEST_EDDI_SELECT_OP_MODE,
            ATTR_OPTION: "Stopped",
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_eddi_set_operating_mode.call_count == 1
    mock_eddi_set_operating_mode.assert_called_with("Stopped")


@contextmanager
def _zappi_reports(zmo: int, cmt: int):
    """Make polls report the given mode and command status for Test Zappi 1."""
    data = copy.deepcopy(load_fixture_json("client"))
    for grp in data["devices"]:
        for device in grp.get("zappi", []):
            if device["sno"] == 16042300:
                device["zmo"] = zmo
                device["cmt"] = cmt
    with (
        patch("pymyenergi.client.MyenergiClient.fetch_data", return_value=data),
        patch(
            "pymyenergi.zappi.Zappi.fetch_history_data",
            return_value=load_fixture_json("history_zappi"),
        ),
        patch(
            "pymyenergi.eddi.Eddi.fetch_history_data",
            return_value=load_fixture_json("history_eddi"),
        ),
    ):
        yield


async def _poll(hass: HomeAssistant, entry, zmo: int, cmt: int = 254) -> None:
    with _zappi_reports(zmo, cmt):
        await hass.data[DOMAIN][entry.entry_id].async_refresh()
        await hass.async_block_till_done()


async def _select_charge_mode(hass: HomeAssistant, option: str) -> None:
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE, ATTR_OPTION: option},
        blocking=True,
    )
    await hass.async_block_till_done()


async def test_zappi_charge_mode_survives_stale_poll(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer
) -> None:
    """A poll taken before the zappi applies the mode must not revert it."""
    entry = await setup_mock_myenergi_config_entry(hass)
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Fast"

    await _select_charge_mode(hass, "Stopped")
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Stopped"

    freezer.tick(timedelta(seconds=10))
    await _poll(hass, entry, zmo=1)
    state = hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE)
    assert state.state == "Stopped"
    assert state.attributes["reported_charge_mode"] == "Fast"
    assert mock_zappi_set_charge_mode.call_count == 1

    freezer.tick(timedelta(seconds=10))
    await _poll(hass, entry, zmo=4)
    state = hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE)
    assert state.state == "Stopped"
    assert "reported_charge_mode" not in state.attributes
    assert mock_zappi_set_charge_mode.call_count == 1


async def test_zappi_charge_mode_resent_when_not_applied(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer
) -> None:
    """An unapplied mode is resent, then given up on after the max attempts."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Stopped")

    for attempt in (2, 3):
        freezer.tick(timedelta(seconds=60))
        await _poll(hass, entry, zmo=1)
        assert mock_zappi_set_charge_mode.call_count == attempt
        mock_zappi_set_charge_mode.assert_called_with("Stopped")
        assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Stopped"

    freezer.tick(timedelta(seconds=60))
    await _poll(hass, entry, zmo=1)
    assert mock_zappi_set_charge_mode.call_count == 3
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Fast"


async def test_zappi_charge_mode_waits_while_command_in_progress(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer
) -> None:
    """No resend while cmt shows the zappi processing a command."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Eco+")

    freezer.tick(timedelta(seconds=60))
    await _poll(hass, entry, zmo=1, cmt=3)
    assert mock_zappi_set_charge_mode.call_count == 1
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Eco+"


async def test_zappi_charge_mode_resent_immediately_on_failure(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock
) -> None:
    """cmt 253 means the command failed, so resend without waiting."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Eco+")

    await _poll(hass, entry, zmo=1, cmt=253)
    assert mock_zappi_set_charge_mode.call_count == 2
