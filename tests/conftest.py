"""Global fixtures for myenergi integration."""
import json
from typing import Any
from unittest.mock import patch

import pytest
from pymyenergi.exceptions import TimeoutException
from pymyenergi.exceptions import WrongCredentials

pytest_plugins = "pytest_homeassistant_custom_component"


def load_fixture_json(name):
    with open(f"tests/fixtures/{name}.json") as json_file:
        data = json.load(json_file)
        return data


@pytest.fixture(name="auto_enable_custom_integrations", autouse=True)
def auto_enable_custom_integrations(
    hass: Any, enable_custom_integrations: Any  # noqa: F811
) -> None:
    """Enable custom integrations defined in the test dir."""


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


# This fixture, when used, will result in calls to async_get_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Mock data from client.fetch_data()"""
    with patch(
        "pymyenergi.client.MyenergiClient.fetch_data",
        return_value=load_fixture_json("client"),
    ), patch(
        "pymyenergi.zappi.Zappi.fetch_history_data",
        return_value=load_fixture_json("history_zappi"),
    ), patch(
        "pymyenergi.eddi.Eddi.fetch_history_data",
        return_value=load_fixture_json("history_eddi"),
    ):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "pymyenergi.client.MyenergiClient.refresh",
        side_effect=Exception,
    ):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="auth_error_on_get_data")
def auth_error_get_data_fixture():
    """Simulate authentication error when retrieving data from API."""
    with patch(
        "pymyenergi.client.MyenergiClient.refresh",
        side_effect=WrongCredentials,
    ):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="timeout_error_on_get_data")
def timeout_error_get_data_fixture():
    """Simulate authentication error when retrieving data from API."""
    with patch(
        "pymyenergi.client.MyenergiClient.refresh",
        side_effect=TimeoutException,
    ):
        yield
