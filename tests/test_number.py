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


async def test_number(hass: HomeAssistant, mock_zappi_set_green: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

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
