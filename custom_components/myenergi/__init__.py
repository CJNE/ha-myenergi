"""
Custom integration to integrate myenergi with Home Assistant.

For more details about this integration, please refer to
https://github.com/cjne/myenergi
"""

import asyncio
import logging
from datetime import timedelta

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from pymyenergi.client import MyenergiClient
from pymyenergi.connection import Connection

from .const import CONF_APP_EMAIL
from .const import CONF_APP_PASSWORD
from .const import CONF_PASSWORD
from .const import CONF_SCAN_INTERVAL
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    app_email = entry.data.get(CONF_APP_EMAIL)
    app_password = entry.data.get(CONF_APP_PASSWORD)

    conn = await hass.async_add_executor_job(
        Connection, username, password, app_password, app_email
    )
    if app_email and app_password:
        await conn.discoverLocations()

    client = MyenergiClient(conn)

    coordinator = MyenergiDataUpdateCoordinator(hass, client=client, entry=entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            await hass.config_entries.async_forward_entry_setups(entry, platform)

    entry.add_update_listener(async_reload_entry)

    # once we reconfigure the integration, we (possibly) need to use the new credentials
    entry.async_on_unload(entry.add_update_listener(config_update_listener))

    return True


class MyenergiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: MyenergiClient, entry) -> None:
        """Initialize."""
        self.client = client
        self.platforms = []

        scan_interval = timedelta(
            seconds=entry.options.get(
                CONF_SCAN_INTERVAL,
                entry.data.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL.total_seconds()),
            )
        )

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=scan_interval)

    async def _async_update_data(self):
        """Update data via library."""
        today = dt_util.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        utc_today = dt_util.as_utc(today)
        _LOGGER.debug(
            f"Refresh history local start of day in UTC {utc_today} {utc_today.tzinfo}"
        )
        try:
            await self.hass.async_add_executor_job(
                self.client._connection.checkAndUpdateToken
            )
            await self.client.refresh()
            await self.client.refresh_history(utc_today, 24, "hour")
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def config_update_listener(hass, entry):
    """Handle options update."""
