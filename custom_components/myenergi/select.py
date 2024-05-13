"""Sensor platform for myenergi."""
import voluptuous as vol
from homeassistant.components.select import SelectEntity
from homeassistant.helpers import entity_platform
from pymyenergi.eddi import EDDI_MODES
from pymyenergi.libbi import LIBBI_MODES
from pymyenergi.zappi import CHARGE_MODES

from .const import DOMAIN
from .entity import MyenergiEntity

LIBBI_MODE_NAMES = {0: "Stopped", 1: "Normal", 5: "Export"}

ZAPPI_PHASE_SETTING = ["1", "3", "auto"]

ATTR_BOOST_AMOUNT = "amount"
ATTR_BOOST_TIME = "time"
ATTR_BOOST_TARGET = "target"
ATTR_BOOST_WHEN = "when"
BOOST_SCHEMA = {
    vol.Required(ATTR_BOOST_AMOUNT): vol.All(
        vol.Coerce(float),
        vol.Range(min=1, max=100),
        vol.Range(min=1, max=100),
    ),
}
EDDI_BOOST_SCHEMA = {
    vol.Required(ATTR_BOOST_TARGET): str,
    vol.Required(ATTR_BOOST_TIME): vol.Coerce(float),
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
            platform.async_register_entity_service(
                "myenergi_stop_boost",
                {},
                "stop_boost",
            )
            platform.async_register_entity_service(
                "myenergi_unlock",
                {},
                "unlock",
            )
            devices.append(ZappiChargeModeSelect(coordinator, device, entry))
            devices.append(ZappiPhaseSettingSelect(coordinator, device, entry))
        elif device.kind == "eddi":
            platform.async_register_entity_service(
                "myenergi_eddi_boost",
                EDDI_BOOST_SCHEMA,
                "start_eddi_boost",
            )
            devices.append(EddiOperatingModeSelect(coordinator, device, entry))
        elif device.kind == "libbi":
            devices.append(LibbiOperatingModeSelect(coordinator, device, entry))
    async_add_devices(devices)


class EddiOperatingModeSelect(MyenergiEntity, SelectEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry):
        super().__init__(coordinator, device, config_entry)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return (
            f"{self.config_entry.entry_id}-{self.device.serial_number}-operating_mode"
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} Operating Mode"

    @property
    def current_option(self):
        """Return the state of the sensor."""
        if self.device.status == "Stopped":
            return "Stopped"
        return "Normal"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.device.set_operating_mode(option)
        self.async_schedule_update_ha_state()

    @property
    def options(self):
        return EDDI_MODES


class ZappiPhaseSettingSelect(MyenergiEntity, SelectEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry):
        super().__init__(coordinator, device, config_entry)
        self._attr_icon = "mdi:ev-station"
        self._attr_unique_id = f"{self.config_entry.entry_id}-{self.device.serial_number}-phase_setting_select"
        self._attr_name = f"myenergi {self.device.name} Phase Setting"
        self._attr_translation_key = "phase_setting"
        self._attr_options = ZAPPI_PHASE_SETTING

    @property
    def current_option(self):
        """Return the state of the sensor."""
        return self.device.num_phases

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.device.set_phase_setting(option)
        self.async_schedule_update_ha_state()


class ZappiChargeModeSelect(MyenergiEntity, SelectEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry):
        super().__init__(coordinator, device, config_entry)
        self._attr_icon = "mdi:ev-station"
        self._attr_unique_id = (
            f"{self.config_entry.entry_id}-{self.device.serial_number}-charge_mode"
        )
        self._attr_name = f"myenergi {self.device.name} Charge Mode"
        self._attr_translation_key = "phase_setting"
        self._attr_options = CHARGE_MODES[1:]

    @property
    def current_option(self):
        """Return the state of the sensor."""
        return self.device.charge_mode

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.device.set_charge_mode(option)
        self.async_schedule_update_ha_state()


class LibbiOperatingModeSelect(MyenergiEntity, SelectEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry):
        super().__init__(coordinator, device, config_entry)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return (
            f"{self.config_entry.entry_id}-{self.device.serial_number}-operating_mode"
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} Operating Mode"

    @property
    def current_option(self):
        """Return the state of the sensor."""
        mode = self.device.local_mode
        return LIBBI_MODE_NAMES[mode]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.device.set_operating_mode(option)
        self.async_schedule_update_ha_state()

    @property
    def options(self):
        return LIBBI_MODES
