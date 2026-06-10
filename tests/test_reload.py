"""Test config-entry reload behaviour.

Regression test for the options-update reload path. Previously the reload
listener was registered without tracking its unsub handle (leaking a fresh
listener on every setup) and reload was hand-rolled as unload+setup, which
could race and strand the coordinator without a running refresh loop. The fix
registers the listener via async_on_unload and delegates reload to the
config-entries manager.
"""

from unittest.mock import AsyncMock
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.myenergi import async_reload_entry
from custom_components.myenergi.const import DOMAIN

from .const import MOCK_CONFIG


async def test_reload_delegates_to_config_entries_manager(hass):
    """async_reload_entry delegates to hass.config_entries.async_reload.

    The manager serialises unload/setup and rebuilds the coordinator (and its
    refresh scheduler) cleanly. The integration must not hand-roll the cycle as
    unload+setup, which could race on an options update and strand the
    coordinator without a running poll loop.
    """
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    with patch.object(
        hass.config_entries, "async_reload", new=AsyncMock()
    ) as mock_reload:
        await async_reload_entry(hass, config_entry)

    mock_reload.assert_awaited_once_with(config_entry.entry_id)
