"""Test myenergi sensor."""
from homeassistant.core import HomeAssistant

from . import setup_mock_myenergi_config_entry

TEST_HUB_SENSOR_POWER_GRID_ENTITY_ID = "sensor.myenergi_test_site_power_grid"


async def test_sensor(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    entity_state = hass.states.get(TEST_HUB_SENSOR_POWER_GRID_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "4429"
