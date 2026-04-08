"""Test myenergi sensor."""

from unittest.mock import MagicMock, PropertyMock, patch

from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import SERVICE_SET_VALUE
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from pymyenergi.libbi import Libbi

from . import setup_mock_myenergi_config_entry

TEST_ZAPPI_NUMBER_GREEN_LEVEL = "number.myenergi_test_zappi_1_minimum_green_level"
TEST_EDDI_NUMBER_HEATER_PRIORITY = "number.myenergi_test_eddi_1_heater_priority"
TEST_EDDI_NUMBER_DEVICE_PRIORITY = "number.myenergi_test_eddi_1_device_priority"
TEST_LIBBI_NUMBER_CHARGE_TARGET = "number.myenergi_test_libbi_1_charge_target"


async def test_number(hass: HomeAssistant, mock_zappi_set_green: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    entity_state = hass.states.get(TEST_ZAPPI_NUMBER_GREEN_LEVEL)
    assert entity_state
    assert entity_state.state == "50"
    assert mock_zappi_set_green.call_count == 0
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_NUMBER_GREEN_LEVEL,
            "value": "58",
        },
        blocking=False,
    )
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
    assert mock_eddi_heater.call_count == 0
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: TEST_EDDI_NUMBER_HEATER_PRIORITY,
            "value": "2",
        },
        blocking=False,
    )
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
    assert mock_eddi_device.call_count == 0
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: TEST_EDDI_NUMBER_DEVICE_PRIORITY,
            "value": "3",
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_eddi_device.call_count == 1
    mock_eddi_device.assert_called_with(3)


async def test_libbi_charge_target_reads_100_percent(hass: HomeAssistant) -> None:
    """Verify charge target entity reads 100% when energyTarget = 18400 Wh (mbc=20400)."""
    with patch.object(Libbi, "charge_target", new_callable=PropertyMock, return_value=18.4):
        await setup_mock_myenergi_config_entry(hass, data={"client_data": "client_libbi"})

    entity_state = hass.states.get(TEST_LIBBI_NUMBER_CHARGE_TARGET)
    assert entity_state
    assert entity_state.state == "100"


async def test_libbi_charge_target_reads_70_percent(hass: HomeAssistant) -> None:
    """Verify charge target entity reads 70% when energyTarget = 12880 Wh (mbc=20400)."""
    with patch.object(Libbi, "charge_target", new_callable=PropertyMock, return_value=12.88):
        await setup_mock_myenergi_config_entry(hass, data={"client_data": "client_libbi"})

    entity_state = hass.states.get(TEST_LIBBI_NUMBER_CHARGE_TARGET)
    assert entity_state
    assert entity_state.state == "70"


async def test_libbi_charge_target_no_credentials_shows_unknown(hass: HomeAssistant) -> None:
    """Verify charge target entity shows unknown state when app credentials are absent."""
    with patch.object(Libbi, "charge_target", new_callable=PropertyMock, return_value=None):
        await setup_mock_myenergi_config_entry(hass, data={"client_data": "client_libbi"})

    entity_state = hass.states.get(TEST_LIBBI_NUMBER_CHARGE_TARGET)
    assert entity_state
    assert entity_state.state == STATE_UNKNOWN


async def test_libbi_set_charge_target_70_percent(
    hass: HomeAssistant, mock_libbi_set_charge_target: MagicMock
) -> None:
    """Verify setting 70% sends 12880 Wh to the API (mbc=20400, usable=18400 Wh)."""
    await setup_mock_myenergi_config_entry(hass, data={"client_data": "client_libbi"})

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: TEST_LIBBI_NUMBER_CHARGE_TARGET, "value": "70"},
        blocking=False,
    )
    await hass.async_block_till_done()
    mock_libbi_set_charge_target.assert_called_once_with(12880)


async def test_libbi_set_charge_target_100_percent(
    hass: HomeAssistant, mock_libbi_set_charge_target: MagicMock
) -> None:
    """Verify setting 100% sends 18400 Wh to the API (mbc=20400, usable=18400 Wh)."""
    await setup_mock_myenergi_config_entry(hass, data={"client_data": "client_libbi"})

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: TEST_LIBBI_NUMBER_CHARGE_TARGET, "value": "100"},
        blocking=False,
    )
    await hass.async_block_till_done()
    mock_libbi_set_charge_target.assert_called_once_with(18400)
