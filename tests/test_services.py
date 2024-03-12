"""Test myenergi sensor."""
from unittest.mock import MagicMock

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from . import setup_mock_myenergi_config_entry

TEST_ZAPPI_SELECT_CHARGE_MODE = "select.myenergi_test_zappi_1_charge_mode"
TEST_EDDI_SELECT_OP_MODE = "select.myenergi_test_eddi_1_operating_mode"


async def test_boost(hass: HomeAssistant, mock_zappi_start_boost: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    await hass.services.async_call(
        "myenergi",
        "myenergi_boost",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
            "amount": "44",
        },
        blocking=False,
    )
    assert mock_zappi_start_boost.call_count == 0
    await hass.async_block_till_done()
    assert mock_zappi_start_boost.call_count == 1
    mock_zappi_start_boost.assert_called_with(44.0)


async def test_smart_boost(
    hass: HomeAssistant, mock_zappi_start_smart_boost: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    await hass.services.async_call(
        "myenergi",
        "myenergi_smart_boost",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
            "amount": "11",
            "when": "12:13:14",
        },
        blocking=False,
    )
    assert mock_zappi_start_smart_boost.call_count == 0
    await hass.async_block_till_done()
    assert mock_zappi_start_smart_boost.call_count == 1
    mock_zappi_start_smart_boost.assert_called_with(11.0, "1213")


async def test_eddi_boost(
    hass: HomeAssistant, mock_eddi_manual_boost: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    await hass.services.async_call(
        "myenergi",
        "myenergi_eddi_boost",
        {ATTR_ENTITY_ID: TEST_EDDI_SELECT_OP_MODE, "target": "Heater 1", "time": 44},
        blocking=False,
    )
    assert mock_eddi_manual_boost.call_count == 0
    await hass.async_block_till_done()
    assert mock_eddi_manual_boost.call_count == 1
    mock_eddi_manual_boost.assert_called_with("Heater 1", 44.0)


async def test_stop_boost(
    hass: HomeAssistant, mock_zappi_stop_boost: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    await hass.services.async_call(
        "myenergi",
        "myenergi_stop_boost",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
        },
        blocking=False,
    )
    assert mock_zappi_stop_boost.call_count == 0
    await hass.async_block_till_done()
    assert mock_zappi_stop_boost.call_count == 1


async def test_unlock(hass: HomeAssistant, mock_zappi_unlock: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    await hass.services.async_call(
        "myenergi",
        "myenergi_unlock",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
        },
        blocking=False,
    )
    assert mock_zappi_unlock.call_count == 0
    await hass.async_block_till_done()
    assert mock_zappi_unlock.call_count == 1
