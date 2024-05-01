"""Switch platform for myenergi."""
import logging
import operator

from homeassistant.components.switch import SwitchEntity
from pymyenergi import LIBBI

from .const import DOMAIN
from .entity import MyenergiEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    # Don't cause a refresh when fetching sensors
    all_devices = await coordinator.client.get_devices("all", False)
    for device in all_devices:
        if device.kind == LIBBI:
            sensors.append(
                MyenergiSwitch(
                    coordinator,
                    device,
                    entry,
                    {
                        "name": "Charge from grid",
                        "prop_name": "charge_from_grid",
                        "icon": "mdi:transmission-tower-import",
                        "update_func": "set_charge_from_grid",
                        "attrs": {},
                    },
                )
            )
    async_add_devices(sensors)


class MyenergiSwitch(MyenergiEntity, SwitchEntity):
    """myenergi Switch class."""

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

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        _LOGGER.debug("libbi charging from grid is now ON")
        _LOGGER.debug(type(self))
        await operator.methodcaller(self.meta["update_func"], True)(self.device)
        self.async_schedule_update_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        _LOGGER.debug("libbi charging from grid is now OFF")
        await operator.methodcaller(self.meta["update_func"], False)(self.device)
        self.async_schedule_update_ha_state()
