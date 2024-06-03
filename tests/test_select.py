"""Test myenergi sensor."""
from unittest.mock import MagicMock

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_OPTION
from homeassistant.const import SERVICE_SELECT_OPTION
from homeassistant.core import HomeAssistant

from . import setup_mock_myenergi_config_entry

TEST_ZAPPI_SELECT_CHARGE_MODE = "select.myenergi_test_zappi_1_charge_mode"
TEST_ZAPPI_SELECT_PHASE_SETTING = "select.myenergi_test_zappi_1_phase_setting"
TEST_EDDI_SELECT_OP_MODE = "select.myenergi_test_eddi_1_operating_mode"


async def test_zappi_select(
    hass: HomeAssistant, mock_zappi_set_phase_setting: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_PHASE_SETTING,
            ATTR_OPTION: "1",
        },
        blocking=False,
    )
    assert mock_zappi_set_phase_setting.call_count == 0
    await hass.async_block_till_done()
    assert mock_zappi_set_phase_setting.call_count == 1
    mock_zappi_set_phase_setting.assert_called_with("1")


async def test_zappi_phaseselect(
    hass: HomeAssistant, mock_zappi_set_charge_mode: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
            ATTR_OPTION: "Eco+",
        },
        blocking=False,
    )
    assert mock_zappi_set_charge_mode.call_count == 0
    await hass.async_block_till_done()
    assert mock_zappi_set_charge_mode.call_count == 1
    mock_zappi_set_charge_mode.assert_called_with("Eco+")


async def test_eddi_select(
    hass: HomeAssistant, mock_eddi_set_operating_mode: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: TEST_EDDI_SELECT_OP_MODE,
            ATTR_OPTION: "Stopped",
        },
        blocking=False,
    )
    assert mock_eddi_set_operating_mode.call_count == 0
    await hass.async_block_till_done()
    assert mock_eddi_set_operating_mode.call_count == 1
    mock_eddi_set_operating_mode.assert_called_with("Stopped")
