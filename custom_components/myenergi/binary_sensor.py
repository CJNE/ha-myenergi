"""Sensor platform for myenergi."""
import operator

from homeassistant.components.binary_sensor import BinarySensorEntity
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
