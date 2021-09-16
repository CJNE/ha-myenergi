"""Test myenergi sensor."""
from unittest.mock import MagicMock

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from . import setup_mock_myenergi_config_entry

TEST_ZAPPI_SELECT_CHARGE_MODE = "select.myenergi_test_zappi_1_charge_mode"


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
