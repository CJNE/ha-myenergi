"""Constants for myenergi."""

# Base component constants
NAME = "myenergi"
DOMAIN = "myenergi"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.28-pre"

ATTRIBUTION = "Data provided by myenergi"
ISSUE_URL = "https://github.com/CJNE/ha-myenergi/issues"

# Icons
ICON = "mdi:format-quote-close"

# Platforms
SENSOR = "sensor"
BINARY_SENSOR = "binary_sensor"
SELECT = "select"
NUMBER = "number"
SWITCH = "switch"
PLATFORMS = [SENSOR, BINARY_SENSOR, SELECT, NUMBER, SWITCH]


# Configuration and options
CONF_SCAN_INTERVAL = "scan_interval"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_APP_EMAIL = "app_email"
CONF_APP_PASSWORD = "app_password"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
