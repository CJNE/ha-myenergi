"""Sensor platform for myenergi."""

import operator

from homeassistant.components.binary_sensor import BinarySensorEntity
from pymyenergi import EDDI
from pymyenergi import ZAPPI

from .const import DOMAIN
from .entity import MyenergiEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []
    # Don't cause a refresh when fetching sensors
    all_devices = await coordinator.client.get_devices("all", False)
    for device in all_devices:
        # Sensors available in all devices
        if device.kind in [ZAPPI]:
            sensors.append(
                MyenergiBinarySensor(
                    coordinator,
                    device,
                    entry,
                    {
                        "name": "Update available",
                        "prop_name": "update_available",
                        "icon": None,
                        "attrs": {},
                    },
                )
            )
            sensors.append(
                MyenergiBinarySensor(
                    coordinator,
                    device,
                    entry,
                    {
                        "name": "Charge When Locked",
                        "prop_name": "charge_when_locked",
                        "icon": None,
                        "attrs": {},
                    },
                )
            )
            sensors.append(
                MyenergiBinarySensor(
                    coordinator,
                    device,
                    entry,
                    {
                        "name": "Locked",
                        "prop_name": "locked",
                        "icon": None,
                        "attrs": {},
                    },
                )
            )
            sensors.append(
                MyenergiBinarySensor(
                    coordinator,
                    device,
                    entry,
                    {
                        "name": "Lock when Plugged In",
                        "prop_name": "lock_when_pluggedin",
                        "icon": None,
                        "attrs": {},
                    },
                )
            )
            sensors.append(
                MyenergiBinarySensor(
                    coordinator,
                    device,
                    entry,
                    {
                        "name": "Lock when Unplugged",
                        "prop_name": "lock_when_unplugged",
                        "icon": None,
                        "attrs": {},
                    },
                )
            )
        if device.kind == EDDI:
            sensors.append(
                MyenergiBinarySensor(
                    coordinator,
                    device,
                    entry,
                    {
                        "name": "Relay 1",
                        "prop_name": "r1a",
                        "icon": None,
                        "attrs": {},
                    },
                )
            )
            sensors.append(
                MyenergiBinarySensor(
                    coordinator,
                    device,
                    entry,
                    {
                        "name": "Relay 2",
                        "prop_name": "r2a",
                        "icon": None,
                        "attrs": {},
                    },
                )
            )
    async_add_devices(sensors)


class MyenergiBinarySensor(MyenergiEntity, BinarySensorEntity):
    """myenergi Binary Sensor class."""

    def __init__(self, coordinator, device, config_entry, meta):
        super().__init__(coordinator, device, config_entry, meta)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} {self.meta['name']}"

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.device.serial_number}-{self.meta['prop_name']}"

    @property
    def is_on(self):
        """Return the state of the sensor."""
        value = operator.attrgetter(self.meta["prop_name"])(self.device)
        return value

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self.meta["icon"]

    @property
    def locked(self):
        """Lock status"""
        return self._data.get("lck", 0) >> 1 & 1 == 1

    @property
    def lock_when_pluggedin(self):
        """Lock when plugged in status"""
        return self._data.get("lck", 0) >> 2 & 1 == 1

    @property
    def lock_when_unplugged(self):
        """Lock when unplugged status"""
        return self._data.get("lck", 0) >> 3 & 1 == 1

    @property
    def charge_when_locked(self):
        """Charge when locked enabled"""
        return self._data.get("lck", 0) >> 4 & 1 == 1
