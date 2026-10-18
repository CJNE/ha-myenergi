"""Test myenergi sensor."""

import copy
import logging
from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

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
def _device_reports(kind: str, sno: int, **fields):
    """Make polls report the given fields for one device."""
    data = copy.deepcopy(load_fixture_json("client"))
    for grp in data["devices"]:
        for device in grp.get(kind, []):
            if device["sno"] == sno:
                device.update(fields)
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


async def _poll_device(hass: HomeAssistant, entry, kind: str, sno: int, **fields):
    with _device_reports(kind, sno, **fields):
        await hass.data[DOMAIN][entry.entry_id].async_refresh()
        await hass.async_block_till_done()


async def _poll(hass: HomeAssistant, entry, zmo: int, cmt: int = 254) -> None:
    await _poll_device(hass, entry, "zappi", 16042300, zmo=zmo, cmt=cmt)


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
        freezer.tick(timedelta(minutes=2))
        await _poll(hass, entry, zmo=1)
        assert mock_zappi_set_charge_mode.call_count == attempt
        mock_zappi_set_charge_mode.assert_called_with("Stopped")
        assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Stopped"

    freezer.tick(timedelta(minutes=2))
    await _poll(hass, entry, zmo=1)
    assert mock_zappi_set_charge_mode.call_count == 3
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Fast"


@pytest.mark.parametrize("cmt", [3, 11, 50, 252])
async def test_zappi_charge_mode_waits_while_command_in_progress(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer, cmt: int
) -> None:
    """No resend while cmt shows the zappi processing a command."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Eco+")

    freezer.tick(timedelta(minutes=4))
    await _poll(hass, entry, zmo=1, cmt=cmt)
    assert mock_zappi_set_charge_mode.call_count == 1
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Eco+"


async def test_zappi_charge_mode_resent_after_pending_timeout(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer
) -> None:
    """A command still in progress after the timeout is resent."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Eco+")

    freezer.tick(timedelta(minutes=5))
    await _poll(hass, entry, zmo=1, cmt=60)
    assert mock_zappi_set_charge_mode.call_count == 2
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Eco+"


async def test_zappi_charge_mode_waits_for_each_resend(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer
) -> None:
    """A resend still in progress is waited for, however long ago the first was."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Eco+")

    for attempt in (2, 3):
        freezer.tick(timedelta(seconds=258))
        await _poll(hass, entry, zmo=1, cmt=253)
        assert mock_zappi_set_charge_mode.call_count == attempt

    freezer.tick(timedelta(minutes=2))
    await _poll(hass, entry, zmo=1, cmt=24)
    assert mock_zappi_set_charge_mode.call_count == 3
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Eco+"

    freezer.tick(timedelta(minutes=1))
    await _poll(hass, entry, zmo=3)
    state = hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE)
    assert state.state == "Eco+"
    assert "reported_charge_mode" not in state.attributes


async def test_zappi_charge_mode_logs_progress(
    hass: HomeAssistant,
    mock_zappi_set_charge_mode: MagicMock,
    freezer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Each step of a pending change is logged for debugging."""
    caplog.set_level(logging.DEBUG, logger="custom_components.myenergi")
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Eco+")
    assert (
        "charge mode Eco+ requested, reports Fast (cmt 254, device time 18:45:19)"
        in caplog.text
    )

    freezer.tick(timedelta(seconds=40))
    await _poll(hass, entry, zmo=1, cmt=8)
    assert (
        "waiting for charge mode Eco+, reports Fast "
        "(cmt 8, device time 18:45:19, attempt 1, 40s since first send, "
        "40s since last)" in caplog.text
    )

    freezer.tick(timedelta(seconds=20))
    await _poll(hass, entry, zmo=3)
    assert (
        "reports charge mode Eco+ (cmt 254, device time 18:45:19, attempt 1, "
        "60s since first send, 60s since last), done waiting for Eco+" in caplog.text
    )


async def test_zappi_charge_mode_stale_result_does_not_skip_wait(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer
) -> None:
    """cmt still shows the previous result until myenergi start on a send."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Eco+")

    freezer.tick(timedelta(seconds=60))
    await _poll(hass, entry, zmo=1, cmt=253)
    assert mock_zappi_set_charge_mode.call_count == 1

    freezer.tick(timedelta(seconds=30))
    await _poll(hass, entry, zmo=1, cmt=18)
    freezer.tick(timedelta(minutes=3))
    await _poll(hass, entry, zmo=1, cmt=253)
    assert mock_zappi_set_charge_mode.call_count == 2

    freezer.tick(timedelta(seconds=60))
    await _poll(hass, entry, zmo=1, cmt=253)
    assert mock_zappi_set_charge_mode.call_count == 2
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Eco+"


async def test_zappi_charge_mode_changed_elsewhere(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer
) -> None:
    """A third mode means it was changed elsewhere, so don't override it."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Stopped")

    freezer.tick(timedelta(seconds=60))
    await _poll(hass, entry, zmo=3)
    assert mock_zappi_set_charge_mode.call_count == 1
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Eco+"


async def test_zappi_charge_mode_failed_poll_is_not_confirmation(
    hass: HomeAssistant, freezer
) -> None:
    """set_charge_mode writes zmo locally, which a failed poll leaves behind."""
    entry = await setup_mock_myenergi_config_entry(hass)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    with patch(
        "pymyenergi.connection.Connection.get", return_value={"status": 0}
    ) as mock_get:
        await _select_charge_mode(hass, "Stopped")
        assert mock_get.call_count == 1

        with patch("pymyenergi.client.MyenergiClient.refresh", side_effect=Exception):
            await coordinator.async_refresh()
            await hass.async_block_till_done()
        assert not coordinator.last_update_success

        freezer.tick(timedelta(minutes=2))
        await _poll(hass, entry, zmo=1)
        assert mock_get.call_count == 2
        assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Stopped"


async def test_zappi_charge_mode_new_selection_replaces_pending(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock, freezer
) -> None:
    """Superseded pending modes still count as not yet applied."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_charge_mode(hass, "Stopped")
    await _select_charge_mode(hass, "Eco+")

    freezer.tick(timedelta(seconds=10))
    await _poll(hass, entry, zmo=4)
    assert hass.states.get(TEST_ZAPPI_SELECT_CHARGE_MODE).state == "Eco+"

    freezer.tick(timedelta(minutes=2))
    await _poll(hass, entry, zmo=4)
    mock_zappi_set_charge_mode.assert_called_with("Eco+")
    assert mock_zappi_set_charge_mode.call_count == 3


async def _select_eddi_mode(hass: HomeAssistant, option: str) -> None:
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: TEST_EDDI_SELECT_OP_MODE, ATTR_OPTION: option},
        blocking=True,
    )
    await hass.async_block_till_done()


async def test_eddi_operating_mode_survives_stale_poll(
    hass: HomeAssistant, mock_eddi_set_operating_mode: MagicMock, freezer
) -> None:
    """A poll taken before the eddi applies the mode must not revert it."""
    entry = await setup_mock_myenergi_config_entry(hass)
    assert hass.states.get(TEST_EDDI_SELECT_OP_MODE).state == "Normal"

    await _select_eddi_mode(hass, "Stopped")
    freezer.tick(timedelta(seconds=10))
    await _poll_device(hass, entry, "eddi", 10088800, sta=1, cmt=254)
    state = hass.states.get(TEST_EDDI_SELECT_OP_MODE)
    assert state.state == "Stopped"
    assert state.attributes["reported_operating_mode"] == "Normal"

    freezer.tick(timedelta(seconds=10))
    await _poll_device(hass, entry, "eddi", 10088800, sta=6, cmt=254)
    state = hass.states.get(TEST_EDDI_SELECT_OP_MODE)
    assert state.state == "Stopped"
    assert "reported_operating_mode" not in state.attributes
    assert mock_eddi_set_operating_mode.call_count == 1


async def test_eddi_operating_mode_resent_when_not_applied(
    hass: HomeAssistant, mock_eddi_set_operating_mode: MagicMock, freezer
) -> None:
    """An unapplied mode is resent, then given up on after the max attempts."""
    entry = await setup_mock_myenergi_config_entry(hass)
    await _select_eddi_mode(hass, "Stopped")

    for attempt in (2, 3):
        freezer.tick(timedelta(minutes=2))
        await _poll_device(hass, entry, "eddi", 10088800, sta=1, cmt=254)
        assert mock_eddi_set_operating_mode.call_count == attempt
        mock_eddi_set_operating_mode.assert_called_with("Stopped")

    freezer.tick(timedelta(minutes=2))
    await _poll_device(hass, entry, "eddi", 10088800, sta=1, cmt=254)
    assert mock_eddi_set_operating_mode.call_count == 3
    assert hass.states.get(TEST_EDDI_SELECT_OP_MODE).state == "Normal"
