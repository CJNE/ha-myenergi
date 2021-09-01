"""MyenergiEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .const import DOMAIN


class MyenergiEntity(CoordinatorEntity):
    def __init__(self, coordinator, device, config_entry):
        super().__init__(coordinator)
        self.device = device
        self.coordinator = coordinator
        self.config_entry = config_entry

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
        return {
            "attribution": ATTRIBUTION,
            # "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }


class MyenergiHub(CoordinatorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

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
        return {
            "attribution": ATTRIBUTION,
            # "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }
