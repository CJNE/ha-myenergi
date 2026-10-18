"""Sensor platform for myenergi."""

import logging
from datetime import timedelta

import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components.select import SelectEntity
from homeassistant.core import callback
from homeassistant.helpers import entity_platform
from pymyenergi.eddi import EDDI_MODES
from pymyenergi.libbi import LIBBI_MODES
from pymyenergi.zappi import CHARGE_MODES

from .const import DOMAIN
from .entity import MyenergiEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)

LIBBI_MODE_NAMES = {"STOP": "Stopped", "BALANCE": "Normal", "DRAIN": "Export"}

ZAPPI_PHASE_SETTING = ["1", "3", "auto"]

# Mode commands are fire-and-forget: the API acknowledges them once queued and
# the myenergi servers relay them to the zappi later, so polls taken in the
# meantime still report the old mode. While a requested mode is unconfirmed we
# keep showing it, and resend it once the last send has finished without the
# zappi applying it.
# Until myenergi start on a send, cmt still shows the previous command's
# result, so a send that hasn't started within this long is treated as lost.
ZAPPI_MODE_START_TIMEOUT = timedelta(minutes=2)
# Stop waiting on a send still in progress this long after it was sent.
# myenergi report failure (cmt 253) about 4 minutes in, so this only applies if
# that never arrives.
ZAPPI_MODE_PENDING_TIMEOUT = timedelta(minutes=5)
ZAPPI_MODE_MAX_ATTEMPTS = 3
# cmt counts up from 1 while a command is in progress (it has been seen above
# 50), then reads 253 on failure, 254 on success or 255 for no command.
ZAPPI_CMT_PENDING = range(1, 253)

ATTR_BOOST_AMOUNT = "amount"
ATTR_BOOST_TIME = "time"
ATTR_BOOST_TARGET = "target"
ATTR_BOOST_WHEN = "when"
ATTR_CHARGE_TARGET = "chargetarget"
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
LIBBI_CHARGE_TARGET_SCHEMA = {
    vol.Required(ATTR_CHARGE_TARGET): vol.All(
        vol.Coerce(float),
        vol.Range(min=0, max=20400),
    )
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
        # libbi services and selects
        elif device.kind == "libbi":
            platform.async_register_entity_service(
                "myenergi_libbi_charge_target",
                LIBBI_CHARGE_TARGET_SCHEMA,
                "libbi_set_charge_target",
            )
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
        self._pending_mode = None
        # Modes a poll may still report while the pending mode is in flight
        self._stale_modes = set()
        self._pending_first_sent_at = None
        self._pending_sent_at = None
        self._pending_attempts = 0
        self._pending_send_started = False
        self._resend_task = None

    @property
    def current_option(self):
        """Return the state of the sensor."""
        if self._pending_mode is not None:
            return self._pending_mode
        return self.device.charge_mode

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        if self._pending_mode is not None:
            attrs["reported_charge_mode"] = self.device.charge_mode
            attrs["charge_mode_attempts"] = self._pending_attempts
        return attrs

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._cancel_resend()
        if self._pending_mode is None:
            self._stale_modes = {self.device.charge_mode}
        else:
            self._stale_modes.add(self._pending_mode)
        self._pending_mode = None
        _LOGGER.debug(
            "%s charge mode %s requested, reports %s (cmt %s, zappi time %s)",
            self.device.name,
            option,
            self.device.charge_mode,
            self.device.data.get("cmt"),
            self.device.time,
        )
        await self.device.set_charge_mode(option)
        self._pending_mode = option
        self._pending_first_sent_at = self._pending_sent_at = dt_util.utcnow()
        self._pending_attempts = 1
        self._pending_send_started = False
        self.async_schedule_update_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """Cancel any pending resend."""
        self._cancel_resend()
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Confirm, hold or retry a pending charge mode on each poll."""
        # A failed poll leaves the locally written mode in place, which would
        # look like a confirmation
        if self._pending_mode is not None and self.coordinator.last_update_success:
            self._check_pending_mode()
        super()._handle_coordinator_update()

    def _check_pending_mode(self) -> None:
        reported = self.device.charge_mode
        cmt = self.device.data.get("cmt")
        now = dt_util.utcnow()
        since_send = now - self._pending_sent_at
        self._pending_send_started |= cmt in ZAPPI_CMT_PENDING
        status = (
            "cmt %s, zappi time %s, attempt %s, %ss since first send, %ss since last"
            % (
                cmt,
                self.device.time,
                self._pending_attempts,
                int((now - self._pending_first_sent_at).total_seconds()),
                int(since_send.total_seconds()),
            )
        )
        # Done once the zappi applies the mode, or it's changed elsewhere
        if reported == self._pending_mode or reported not in self._stale_modes:
            _LOGGER.debug(
                "%s reports charge mode %s (%s), done waiting for %s",
                self.device.name,
                reported,
                status,
                self._pending_mode,
            )
            self._pending_mode = None
            return
        if (cmt in ZAPPI_CMT_PENDING and since_send < ZAPPI_MODE_PENDING_TIMEOUT) or (
            not self._pending_send_started and since_send < ZAPPI_MODE_START_TIMEOUT
        ):
            _LOGGER.debug(
                "%s waiting for charge mode %s, reports %s (%s)",
                self.device.name,
                self._pending_mode,
                reported,
                status,
            )
            return
        if self._pending_attempts >= ZAPPI_MODE_MAX_ATTEMPTS:
            _LOGGER.warning(
                "%s did not change charge mode to %s, it still reports %s (%s)",
                self.device.name,
                self._pending_mode,
                reported,
                status,
            )
            self._pending_mode = None
            return
        _LOGGER.debug(
            "%s reports charge mode %s (%s), resending %s",
            self.device.name,
            reported,
            status,
            self._pending_mode,
        )
        self._pending_attempts += 1
        self._pending_sent_at = now
        self._pending_send_started = False
        self._cancel_resend()
        self._resend_task = self.config_entry.async_create_background_task(
            self.hass,
            self._async_resend_mode(self._pending_mode),
            f"myenergi resend charge mode {self.device.serial_number}",
        )

    @callback
    def _cancel_resend(self) -> None:
        if self._resend_task is not None and not self._resend_task.done():
            self._resend_task.cancel()
        self._resend_task = None

    async def _async_resend_mode(self, mode: str) -> None:
        try:
            await self.device.set_charge_mode(mode)
        except Exception as exception:  # noqa: BLE001
            _LOGGER.warning(
                "Resending charge mode %s to %s failed: %s",
                mode,
                self.device.name,
                exception,
            )


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
        return self.device.get_mode_description(self.device.local_mode)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.device.set_operating_mode(option)
        self.async_schedule_update_ha_state()

    @property
    def options(self):
        return LIBBI_MODES
