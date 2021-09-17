"""Test myenergi sensor."""
from homeassistant.core import HomeAssistant

from . import setup_mock_myenergi_config_entry

TEST_HUB_SENSOR_POWER_GRID_ENTITY_ID = "sensor.myenergi_test_site_power_grid"
TEST_EDDI_SENSOR_TEMP_1_ENTITY_ID = "sensor.myenergi_test_eddi_1_temp_tank_1"
TEST_EDDI_SENSOR_TEMP_2_ENTITY_ID = "sensor.myenergi_test_eddi_1_temp_tank_2"


async def test_sensor(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    entity_state = hass.states.get(TEST_HUB_SENSOR_POWER_GRID_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "4429"


async def test_eddi_temp_sensor(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    print(hass.states)
    entity_state = hass.states.get(TEST_EDDI_SENSOR_TEMP_1_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "49"


async def test_eddi_temp_sensor_2(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    print(hass.states)
    entity_state = hass.states.get(TEST_EDDI_SENSOR_TEMP_2_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "54"
