"""Test myenergi setup process."""

from homeassistant.config_entries import ConfigEntryState
from custom_components.myenergi import (
    MyenergiDataUpdateCoordinator,
)
from custom_components.myenergi.const import (
    DOMAIN,
)

from . import create_mock_myenergi_config_entry


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Setup, reload and unload are driven through the config entries manager so the
# entry transitions through the states (SETUP_IN_PROGRESS -> LOADED) that
# DataUpdateCoordinator.async_config_entry_first_refresh now requires.
async def test_setup_unload_and_reload_entry(hass, bypass_get_data):
    """Test entry setup, reload and unload."""
    config_entry = create_mock_myenergi_config_entry(hass)

    # Set up the entry and assert that the coordinator is stored where we expect.
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], MyenergiDataUpdateCoordinator
    )

    # Reload the entry and assert the coordinator is rebuilt and still present.
    assert await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], MyenergiDataUpdateCoordinator
    )

    # Unload the entry and verify that the data has been removed.
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass, error_on_get_data):
    """Test the entry retries setup when the API raises during first refresh."""
    config_entry = create_mock_myenergi_config_entry(hass)

    # The `error_on_get_data` fixture makes the first refresh fail, which surfaces
    # as ConfigEntryNotReady and leaves the entry in the SETUP_RETRY state.
    assert not await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
