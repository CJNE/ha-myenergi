"""MyenergiEntity class"""

import logging

from homeassistant.helpers.entity import EntityCategory
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
            if self.meta.get("category", None) is not None:
                self.meta["category"] = EntityCategory(self.meta["category"])

    #    async def async_added_to_hass(self):
    #        """Run when about to be added to hass."""
    #        async_dispatcher_connect(
    #            # The Hass Object
    #            self.hass,
    #            # The Signal to listen for.
    #            # Try to make it unique per entity instance
    #            # so include something like entity_id
    #            # or other unique data from the service call
    #            self.entity_id,
    #            # Function handle to call when signal is received
    #            self.libbi_set_charge_target
    #        )
    #        _LOGGER.debug("registered signal with HA")
    #
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.serial_number)},
            "name": self.device.name,
            "model": self.device.kind.capitalize(),
            "manufacturer": "myenergi",
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
        _LOGGER.debug("Start eddi boost called, time %s target %s", time, target)
        """Start eddi boost"""
        await self.device.manual_boost(target, time)
        self.schedule_update_ha_state()

    async def start_smart_boost(self, amount: float, when: str) -> None:
        _LOGGER.debug("Start smart boost called, amount %s when %s", amount, when)
        """Start boost"""
        when = when.replace(":", "")[:4]
        await self.device.start_smart_boost(amount, when)
        self.schedule_update_ha_state()

    async def stop_boost(self) -> None:
        _LOGGER.debug("Stop boost called")
        """Stop boost"""
        await self.device.stop_boost()
        self.schedule_update_ha_state()

    async def unlock(self) -> None:
        _LOGGER.debug("unlock called")
        """Unlock"""
        await self.device.unlock()

    async def libbi_set_charge_target(self, chargetarget: float) -> None:
        _LOGGER.debug("Setting libbi charge target to %s Wh", chargetarget)
        """Set libbi charge target"""
        await self.device.set_charge_target(chargetarget)
        self.schedule_update_ha_state()


class MyenergiHub(CoordinatorEntity):
    def __init__(self, coordinator, config_entry, meta):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.coordinator = coordinator
        self.meta = meta
        if meta is not None:
            if self.meta.get("category", None) is not None:
                self.meta["category"] = EntityCategory(self.meta["category"])

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
