"""Test myenergi sensor."""

from unittest.mock import MagicMock

from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import SERVICE_SET_VALUE
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.core import HomeAssistant

from . import setup_mock_myenergi_config_entry

TEST_ZAPPI_NUMBER_GREEN_LEVEL = "number.myenergi_test_zappi_1_minimum_green_level"
TEST_EDDI_NUMBER_HEATER_PRIORITY = "number.myenergi_test_eddi_1_heater_priority"
TEST_EDDI_NUMBER_DEVICE_PRIORITY = "number.myenergi_test_eddi_1_device_priority"


async def test_number(hass: HomeAssistant, mock_zappi_set_green: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    entity_state = hass.states.get(TEST_ZAPPI_NUMBER_GREEN_LEVEL)
    assert entity_state
    assert entity_state.state == "50"
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_NUMBER_GREEN_LEVEL,
            "value": "58",
        },
        blocking=False,
    )
    assert mock_zappi_set_green.call_count == 0
    await hass.async_block_till_done()
    assert mock_zappi_set_green.call_count == 1
    mock_zappi_set_green.assert_called_with(58)


async def test_heater_priority(
    hass: HomeAssistant, mock_eddi_heater: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    entity_state = hass.states.get(TEST_EDDI_NUMBER_HEATER_PRIORITY)
    assert entity_state
    assert entity_state.state == "1"
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: TEST_EDDI_NUMBER_HEATER_PRIORITY,
            "value": "2",
        },
        blocking=False,
    )
    assert mock_eddi_heater.call_count == 0
    await hass.async_block_till_done()
    assert mock_eddi_heater.call_count == 1
    mock_eddi_heater.assert_called_with("heater2")


async def test_device_priority(
    hass: HomeAssistant, mock_eddi_device: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    entity_state = hass.states.get(TEST_EDDI_NUMBER_DEVICE_PRIORITY)
    assert entity_state
    assert entity_state.state == "2"
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: TEST_EDDI_NUMBER_DEVICE_PRIORITY,
            "value": "3",
        },
        blocking=False,
    )
    assert mock_eddi_device.call_count == 0
    await hass.async_block_till_done()
    assert mock_eddi_device.call_count == 1
    mock_eddi_device.assert_called_with(3)
