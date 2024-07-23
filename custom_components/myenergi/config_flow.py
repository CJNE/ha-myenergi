"""Adds config flow for myenergi."""

import logging
import traceback

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import NumberSelector
from homeassistant.helpers.selector import NumberSelectorConfig
from pymyenergi.client import MyenergiClient
from pymyenergi.connection import Connection
from pymyenergi.exceptions import TimeoutException
from pymyenergi.exceptions import WrongCredentials

from . import SCAN_INTERVAL
from .const import CONF_PASSWORD
from .const import CONF_SCAN_INTERVAL
from .const import CONF_USERNAME
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class MyenergiFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for myenergi."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            err, client = await self._test_credentials(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            if client:
                return self.async_create_entry(title=client.site_name, data=user_input)
            self._errors["base"] = err

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MyenergiOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        defaults = user_input or {CONF_USERNAME: "", CONF_PASSWORD: ""}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=defaults[CONF_USERNAME]): str,
                    vol.Required(CONF_PASSWORD, default=defaults[CONF_PASSWORD]): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username, password):
        """Return true if credentials is valid."""
        _LOGGER.debug("Test myenergi credentials")
        try:
            conn = Connection(username, password)
            client = MyenergiClient(conn)
            await client.refresh()
            return None, client
        except WrongCredentials:
            error = "auth"
        except TimeoutException:
            _LOGGER.error("Timeout when communicating with myenergi servers")
            error = "connection_timeout"
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.error(
                "".join(traceback.format_exception(ex, value=ex, tb=ex.__traceback__))
            )
            error = "connection"
        return error, None


class MyenergiOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for myenergi."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, SCAN_INTERVAL.total_seconds()
        )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=scan_interval
                    ): NumberSelector(
                        NumberSelectorConfig(min=1, max=300, step=1),
                    ),
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get("Hub " + CONF_USERNAME), data=self.options
        )
