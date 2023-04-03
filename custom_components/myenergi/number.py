"""Sensor platform for myenergi."""
from homeassistant.components.number import NumberEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .entity import MyenergiEntity

ENTITY_CATEGORY_CONFIG = EntityCategory.CONFIG


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup number platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices = []
    # Don't cause a refresh when fetching devices
    all_devices = await coordinator.client.get_devices("all", False)
    for device in all_devices:
        # Zappi only numbers
        if device.kind == "zappi":
            devices.append(MinimumGreenLevelNumber(coordinator, device, entry))
            devices.append(DevicePriorityNumber(coordinator, device, entry))
        elif device.kind == "eddi":
            devices.append(HeaterPriorityNumber(coordinator, device, entry))
            devices.append(DevicePriorityNumber(coordinator, device, entry))
    async_add_devices(devices)


class HeaterPriorityNumber(MyenergiEntity, NumberEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry):
        super().__init__(
            coordinator,
            device,
            config_entry,
            {"attrs": {}, "category": ENTITY_CATEGORY_CONFIG},
        )

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return (
            f"{self.config_entry.entry_id}-{self.device.serial_number}-heater_priority"
        )

    @property
    def entity_category(self):
        return self.meta["category"]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} Heater Priority"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.device.heater_priority

    async def async_set_native_value(self, value: float) -> None:
        """Change the selected option."""
        await self.device.set_heater_priority(f"heater{int(value)}")
        self.async_schedule_update_ha_state()

    @property
    def native_min_value(self):
        return 1

    @property
    def native_max_value(self):
        return 2

    @property
    def native_step(self):
        return 1


class DevicePriorityNumber(MyenergiEntity, NumberEntity):
    """myenergi number class."""

    def __init__(self, coordinator, device, config_entry):
        super().__init__(
            coordinator,
            device,
            config_entry,
            {"attrs": {}, "category": ENTITY_CATEGORY_CONFIG},
        )

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return (
            f"{self.config_entry.entry_id}-{self.device.serial_number}-device_priority"
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} Device Priority"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.device.priority

    async def async_set_native_value(self, value: float) -> None:
        """Change the selected option."""
        await self.device.set_priority(int(value))
        self.async_schedule_update_ha_state()

    @property
    def icon(self):
        """Return the icon of the select."""
        return "mdi:sort-numeric-variant"

    @property
    def native_min_value(self):
        return 1

    @property
    def native_max_value(self):
        return 10

    @property
    def native_step(self):
        return 1


class MinimumGreenLevelNumber(MyenergiEntity, NumberEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry):
        super().__init__(
            coordinator,
            device,
            config_entry,
            {"attrs": {}, "category": ENTITY_CATEGORY_CONFIG},
        )

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.device.serial_number}-minimum_green_level"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} Minimum Green Level"

    @property
    def icon(self):
        """Return the icon of the select."""
        return "mdi:leaf"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.device.minimum_green_level

    async def async_set_native_value(self, value: float) -> None:
        """Change the selected option."""
        await self.device.set_minimum_green_level(int(value))
        self.async_schedule_update_ha_state()

    @property
    def native_min_value(self):
        return 0

    @property
    def native_max_value(self):
        return 100

    @property
    def native_step(self):
        return 1
