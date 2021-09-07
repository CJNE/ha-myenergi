"""Constants for myenergi."""
# Base component constants
NAME = "myenergi"
DOMAIN = "myenergi"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.9"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/cjne/myenergi/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
SENSOR = "sensor"
SELECT = "select"
NUMBER = "number"
PLATFORMS = [SENSOR, SELECT, NUMBER]


# Configuration and options
CONF_SCAN_INTERVAL = "scan_interval"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

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
