"""MyenergiEntity class"""
import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


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
    def entity_category(self):
        return self.meta.get("category", None)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            "integration": DOMAIN,
        }
        return {**attrs, **self.meta["attrs"]}

    async def start_boost(self, amount: float) -> None:
        _LOGGER.debug("Start boost called, amount %s", amount)
        """Start boost"""
        await self.device.start_boost(amount)
        self.schedule_update_ha_state()

    async def start_eddi_boost(self, target: str, time: float) -> None:
        _LOGGER.debug("Start eddit boost called, time %s target %s", time, target)
        """Start eddi boost"""
        await self.device.manual_boost(target, time)
        self.schedule_update_ha_state()

    async def start_smart_boost(self, amount: float, when: str) -> None:
        _LOGGER.debug("Start smart boost called, amount %s when %s", amount, when)
        """Start boost"""
        when = when.replace(":", "")[:4]
        await self.device.start_smart_boost(amount, when)
        self.schedule_update_ha_state()


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
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            "integration": DOMAIN,
        }
        return {**attrs, **self.meta["attrs"]}

    @property
    def entity_category(self):
        return self.meta.get("category", None)
