"""Adds config flow for myenergi."""

import logging
import traceback

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import NumberSelector
from homeassistant.helpers.selector import NumberSelectorConfig
from pymyenergi.client import MyenergiClient
from pymyenergi.connection import Connection
from pymyenergi.exceptions import TimeoutException
from pymyenergi.exceptions import WrongCredentials

from . import SCAN_INTERVAL
from .const import CONF_APP_EMAIL
from .const import CONF_APP_PASSWORD
from .const import CONF_PASSWORD
from .const import CONF_SCAN_INTERVAL
from .const import CONF_USERNAME
from .const import DOMAIN


CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
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
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_APP_EMAIL],
                user_input[CONF_APP_PASSWORD],
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
        defaults = user_input or {
            CONF_USERNAME: "",
            CONF_PASSWORD: "",
            CONF_APP_EMAIL: "",
            CONF_APP_PASSWORD: "",
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=defaults[CONF_USERNAME]): str,
                    vol.Required(CONF_PASSWORD, default=defaults[CONF_PASSWORD]): str,
                    vol.Optional(CONF_APP_EMAIL, default=defaults[CONF_APP_EMAIL]): str,
                    vol.Optional(
                        CONF_APP_PASSWORD, default=defaults[CONF_APP_PASSWORD]
                    ): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, username, password, app_email, app_password):
        """Return true if credentials is valid."""
        _LOGGER.debug("Test myenergi credentials")
        try:
            conn = await self.hass.async_add_executor_job(
                Connection, username, password, app_password, app_email
            )
            if app_password and app_email:
                await conn.discoverLocations()
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
            # create a new dict to update config data (don't duplicate it in options)
            cdata = {}
            cdata[CONF_USERNAME] = self.config_entry.data[CONF_USERNAME]
            cdata[CONF_PASSWORD] = self.config_entry.data[CONF_PASSWORD]
            if CONF_APP_EMAIL in user_input:
                cdata[CONF_APP_EMAIL] = user_input[CONF_APP_EMAIL]
                del user_input[CONF_APP_EMAIL]
            if CONF_APP_PASSWORD in user_input:
                cdata[CONF_APP_PASSWORD] = user_input[CONF_APP_PASSWORD]
                del user_input[CONF_APP_PASSWORD]

            # now update config data
            self.hass.config_entries.async_update_entry(self.config_entry, data=cdata)

            # finally update options data (which is now only the SCAN_INTERVAL)
            self.options.update(user_input)
            return await self._update_options()

        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, SCAN_INTERVAL.total_seconds()
        )
        app_email = self.config_entry.options.get(CONF_APP_EMAIL, "")
        app_password = self.config_entry.options.get(CONF_APP_PASSWORD, "")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=scan_interval
                    ): NumberSelector(
                        NumberSelectorConfig(min=1, max=300, step=1),
                    ),
                    vol.Optional(CONF_APP_EMAIL, default=app_email): str,
                    vol.Optional(CONF_APP_PASSWORD, default=app_password): str,
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get("Hub " + CONF_USERNAME), data=self.options
        )
