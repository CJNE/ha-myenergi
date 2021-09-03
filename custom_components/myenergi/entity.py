"""MyenergiEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class MyenergiEntity(CoordinatorEntity):
    def __init__(self, coordinator, device, config_entry, meta=None):
        super().__init__(coordinator)
        self.device = device
        self.coordinator = coordinator
        self.config_entry = config_entry
        if meta is None:
            self.meta = {"attrs": {}}
        else:
            self.meta = meta

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.serial_number)},
            "name": self.device.name,
            "model": self.device.kind.capitalize(),
            "manufacturer": "myenergi",
            "via_device": self.coordinator.client.serial_number,
            "sw_version": self.device.firmware_version,
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            "integration": DOMAIN,
        }
        return {**attrs, **self.meta["attrs"]}


class MyenergiHub(CoordinatorEntity):
    def __init__(self, coordinator, config_entry, meta):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.coordinator = coordinator
        self.meta = meta

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.client.serial_number)},
            "name": self.coordinator.client.site_name,
            "model": "Hub",
            "manufacturer": "myenergi",
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            "integration": DOMAIN,
        }
        return {**attrs, **self.meta["attrs"]}
