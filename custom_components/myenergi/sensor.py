"""Sensor platform for myenergi."""
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import SENSOR
from .entity import MyenergiEntity


def create_meta(name, prop_name, device_class=None, unit=None, icon=None):
    """Create metadata for entity"""
    return {'name': name, 'prop_name': prop_name, 'device_class': device_class, 'unit': unit, 'icon': icon}


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices = []
    all_devices = await coordinator.api.get_devices()
    for device in all_devices:
        if(device.kind in ['zappi', 'eddi']):
            devices.append(MyenergiSensor(coordinator, device, entry, create_meta("Status", "status")))

    async_add_devices(devices)


class MyenergiSensor(MyenergiEntity):
    """myenergi Sensor class."""
    def __init__(self, coordinator, device, config_entry, meta):
        super().__init__(coordinator, device, config_entry)
        self.meta = meta

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.device.serial_number}-{self.meta['prop_name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.meta['name']

    @property
    def state(self):
        """Return the state of the sensor."""
        return getattr(self.device, self.meta['prop_name'])

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self.meta['icon']

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return self.meta['device_class']
