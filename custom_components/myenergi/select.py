"""Sensor platform for myenergi."""
import voluptuous as vol
from homeassistant.components.select import SelectEntity
from homeassistant.helpers import entity_platform
from pymyenergi.zappi import CHARGE_MODES

from .const import DOMAIN
from .entity import MyenergiEntity

ATTR_BOOST_AMOUNT = "amount"
ATTR_BOOST_WHEN = "when"
BOOST_SCHEMA = {
    vol.Required(ATTR_BOOST_AMOUNT): vol.All(
        vol.Coerce(float), vol.Range(min=1, max=100)
    ),
}
SMART_BOOST_SCHEMA = {
    vol.Required(ATTR_BOOST_AMOUNT): vol.All(
        vol.Coerce(float),
        vol.Range(min=1, max=100),
    ),
    vol.Required(ATTR_BOOST_WHEN): str,
}


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    platform = entity_platform.async_get_current_platform()
    devices = []
    # Don't cause a refresh when fetching devices
    all_devices = await coordinator.client.get_devices("all", False)
    for device in all_devices:
        # Zappi only selects
        if device.kind == "zappi":
            platform.async_register_entity_service(
                "myenergi_boost",
                BOOST_SCHEMA,
                "start_boost",
            )
            platform.async_register_entity_service(
                "myenergi_smart_boost",
                SMART_BOOST_SCHEMA,
                "start_smart_boost",
            )
            devices.append(ChargeModeSelect(coordinator, device, entry))
    async_add_devices(devices)


class ChargeModeSelect(MyenergiEntity, SelectEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry):
        super().__init__(coordinator, device, config_entry)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.device.serial_number}-charge_mode"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} Charge Mode"

    @property
    def current_option(self):
        """Return the state of the sensor."""
        return self.device.charge_mode

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.device.set_charge_mode(option)
        self.async_schedule_update_ha_state()

    @property
    def options(self):
        return CHARGE_MODES[1:]
