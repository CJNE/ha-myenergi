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
# the myenergi servers relay them to the device later, so polls taken in the
# meantime still report the old option. While a requested option is unconfirmed
# we keep showing it, and resend it once the last send has finished without the
# device applying it.
# Until myenergi start on a send, cmt still shows the previous command's
# result, so a send that hasn't started within this long is treated as lost.
COMMAND_START_TIMEOUT = timedelta(minutes=2)
# Stop waiting on a send still in progress this long after it was sent.
# myenergi report failure (cmt 253) about 4 minutes in, so this only applies if
# that never arrives.
COMMAND_PENDING_TIMEOUT = timedelta(minutes=5)
COMMAND_MAX_ATTEMPTS = 3
# cmt counts up from 1 while a command is in progress (it has been seen above
# 50), then reads 253 on failure, 254 on success or 255 for no command.
CMT_PENDING = range(1, 253)

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


class MyenergiCommandSelect(MyenergiEntity, SelectEntity):
    """Select set by a mode command, shown as requested until a poll confirms it."""

    # Name of the setting in logs and attributes
    _setting = None

    def __init__(self, coordinator, device, config_entry):
        super().__init__(coordinator, device, config_entry)
        self._pending_option = None
        # Options a poll may still report while the pending option is in flight
        self._stale_options = set()
        self._pending_first_sent_at = None
        self._pending_sent_at = None
        self._pending_attempts = 0
        self._pending_send_started = False
        self._resend_task = None

    @property
    def reported_option(self):
        """Return the option the device reports."""
        raise NotImplementedError

    async def _async_send(self, option: str) -> None:
        raise NotImplementedError

    @property
    def current_option(self):
        """Return the state of the sensor."""
        if self._pending_option is not None:
            return self._pending_option
        return self.reported_option

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = super().extra_state_attributes
        if self._pending_option is not None:
            key = self._setting.replace(" ", "_")
            attrs[f"reported_{key}"] = self.reported_option
            attrs[f"{key}_attempts"] = self._pending_attempts
        return attrs

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._cancel_resend()
        if self._pending_option is None:
            self._stale_options = {self.reported_option}
        else:
            self._stale_options.add(self._pending_option)
        self._pending_option = None
        _LOGGER.debug(
            "%s %s %s requested, reports %s (cmt %s, device time %s)",
            self.device.name,
            self._setting,
            option,
            self.reported_option,
            self.device.data.get("cmt"),
            self.device.time,
        )
        await self._async_send(option)
        self._pending_option = option
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
        """Confirm, hold or retry a pending option on each poll."""
        # A failed poll leaves the locally written option in place, which would
        # look like a confirmation
        if self._pending_option is not None and self.coordinator.last_update_success:
            self._check_pending_option()
        super()._handle_coordinator_update()

    def _check_pending_option(self) -> None:
        reported = self.reported_option
        cmt = self.device.data.get("cmt")
        now = dt_util.utcnow()
        since_send = now - self._pending_sent_at
        self._pending_send_started |= cmt in CMT_PENDING
        status = (
            "cmt %s, device time %s, attempt %s, %ss since first send, %ss since last"
            % (
                cmt,
                self.device.time,
                self._pending_attempts,
                int((now - self._pending_first_sent_at).total_seconds()),
                int(since_send.total_seconds()),
            )
        )
        # Done once the device applies the option, or it's changed elsewhere
        if reported == self._pending_option or reported not in self._stale_options:
            _LOGGER.debug(
                "%s reports %s %s (%s), done waiting for %s",
                self.device.name,
                self._setting,
                reported,
                status,
                self._pending_option,
            )
            self._pending_option = None
            return
        if (cmt in CMT_PENDING and since_send < COMMAND_PENDING_TIMEOUT) or (
            not self._pending_send_started and since_send < COMMAND_START_TIMEOUT
        ):
            _LOGGER.debug(
                "%s waiting for %s %s, reports %s (%s)",
                self.device.name,
                self._setting,
                self._pending_option,
                reported,
                status,
            )
            return
        if self._pending_attempts >= COMMAND_MAX_ATTEMPTS:
            _LOGGER.warning(
                "%s did not change %s to %s, it still reports %s (%s)",
                self.device.name,
                self._setting,
                self._pending_option,
                reported,
                status,
            )
            self._pending_option = None
            return
        _LOGGER.debug(
            "%s reports %s %s (%s), resending %s",
            self.device.name,
            self._setting,
            reported,
            status,
            self._pending_option,
        )
        self._pending_attempts += 1
        self._pending_sent_at = now
        self._pending_send_started = False
        self._cancel_resend()
        self._resend_task = self.config_entry.async_create_background_task(
            self.hass,
            self._async_resend(self._pending_option),
            f"myenergi resend {self._setting} {self.device.serial_number}",
        )

    @callback
    def _cancel_resend(self) -> None:
        if self._resend_task is not None and not self._resend_task.done():
            self._resend_task.cancel()
        self._resend_task = None

    async def _async_resend(self, option: str) -> None:
        try:
            await self._async_send(option)
        except Exception as exception:  # noqa: BLE001
            _LOGGER.warning(
                "Resending %s %s to %s failed: %s",
                self._setting,
                option,
                self.device.name,
                exception,
            )


class EddiOperatingModeSelect(MyenergiCommandSelect):
    """myenergi Sensor class."""

    _setting = "operating mode"

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
    def reported_option(self):
        """Return the option the device reports."""
        if self.device.status == "Stopped":
            return "Stopped"
        return "Normal"

    async def _async_send(self, option: str) -> None:
        await self.device.set_operating_mode(option)

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


class ZappiChargeModeSelect(MyenergiCommandSelect):
    """myenergi Sensor class."""

    _setting = "charge mode"

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
    def reported_option(self):
        """Return the option the device reports."""
        return self.device.charge_mode

    async def _async_send(self, option: str) -> None:
        await self.device.set_charge_mode(option)


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
