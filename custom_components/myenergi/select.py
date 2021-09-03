"""Sensor platform for myenergi."""
from homeassistant.components.select import SelectEntity
from pymyenergi.zappi import CHARGE_MODES

from .const import DOMAIN
from .entity import MyenergiEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices = []
    all_devices = await coordinator.client.get_devices()
    for device in all_devices:
        # Zappi only selects
        if device.kind == "zappi":
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
