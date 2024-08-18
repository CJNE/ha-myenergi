"""Test myenergi sensor."""

from homeassistant.core import HomeAssistant

from . import setup_mock_myenergi_config_entry

TEST_HUB_SENSOR_POWER_GRID_ENTITY_ID = "sensor.myenergi_test_site_power_grid"
TEST_HUB_SENSOR_POWER_EXPORT_ENTITY_ID = "sensor.myenergi_test_site_power_export"
TEST_HUB_SENSOR_POWER_IMPORT_ENTITY_ID = "sensor.myenergi_test_site_power_import"
TEST_EDDI_SENSOR_TEMP_1_ENTITY_ID = "sensor.myenergi_test_eddi_1_temp_tank_1"
TEST_EDDI_SENSOR_TEMP_2_ENTITY_ID = "sensor.myenergi_test_eddi_1_temp_tank_2"


async def test_sensor(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    entity_state = hass.states.get(TEST_HUB_SENSOR_POWER_GRID_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "4429"


async def test_sensor_power_import(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    entity_state = hass.states.get(TEST_HUB_SENSOR_POWER_GRID_ENTITY_ID)
    entity_state_import = hass.states.get(TEST_HUB_SENSOR_POWER_IMPORT_ENTITY_ID)
    entity_state_export = hass.states.get(TEST_HUB_SENSOR_POWER_EXPORT_ENTITY_ID)
    assert entity_state
    assert entity_state_import
    assert entity_state_export
    assert entity_state.state == "4429"
    assert entity_state_import.state == "4429"
    assert entity_state_export.state == "0"


async def test_sensor_power_export(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass, {"client_data": "client_exporting"})

    entity_state = hass.states.get(TEST_HUB_SENSOR_POWER_GRID_ENTITY_ID)
    entity_state_import = hass.states.get(TEST_HUB_SENSOR_POWER_IMPORT_ENTITY_ID)
    entity_state_export = hass.states.get(TEST_HUB_SENSOR_POWER_EXPORT_ENTITY_ID)
    assert entity_state
    assert entity_state_import
    assert entity_state_export
    assert entity_state.state == "-1234"
    assert entity_state_import.state == "0"
    assert entity_state_export.state == "1234"


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
