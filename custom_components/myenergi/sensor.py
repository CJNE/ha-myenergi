"""Sensor platform for myenergi."""
import operator

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT
from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING
from homeassistant.const import DEVICE_CLASS_ENERGY
from homeassistant.const import DEVICE_CLASS_POWER
from homeassistant.const import DEVICE_CLASS_TEMPERATURE
from homeassistant.const import DEVICE_CLASS_VOLTAGE
from homeassistant.const import ELECTRIC_POTENTIAL_VOLT
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.const import FREQUENCY_HERTZ
from homeassistant.const import POWER_WATT
from homeassistant.const import TEMP_CELSIUS
from pymyenergi import CT_BATTERY
from pymyenergi import CT_LOAD
from pymyenergi import EDDI
from pymyenergi import HARVI
from pymyenergi import ZAPPI

from .const import DOMAIN
from .entity import MyenergiEntity
from .entity import MyenergiHub


ICON_VOLT = "mdi:lightning-bolt"
ICON_FREQ = "mdi:sine-wave"


def create_meta(
    name, prop_name, device_class=None, unit=None, icon=None, state_class=None
):
    """Create metadata for entity"""
    return {
        "name": name,
        "prop_name": prop_name,
        "device_class": device_class,
        "unit": unit,
        "icon": icon,
        "state_class": state_class,
        "attrs": {},
    }


def create_power_meta(name, prop_name):
    return {
        "name": name,
        "prop_name": prop_name,
        "device_class": DEVICE_CLASS_POWER,
        "unit": POWER_WATT,
        "icon": "mdi:flash",
        "state_class": STATE_CLASS_MEASUREMENT,
        "attrs": {},
    }


def create_energy_meta(name, prop_name):
    return {
        "name": name,
        "prop_name": prop_name,
        "device_class": DEVICE_CLASS_ENERGY,
        "unit": ENERGY_KILO_WATT_HOUR,
        "icon": None,
        "state_class": STATE_CLASS_TOTAL_INCREASING,
        "attrs": {},
    }


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []
    # Don't cause a refresh when fetching sensors
    all_devices = await coordinator.client.get_devices("all", False)
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_power_meta(
                "Power grid",
                "power_grid",
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_power_meta(
                "Power export",
                "power_export",
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_power_meta(
                "Power import",
                "power_import",
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_meta(
                "Voltage grid",
                "voltage_grid",
                DEVICE_CLASS_VOLTAGE,
                ELECTRIC_POTENTIAL_VOLT,
                ICON_VOLT,
                STATE_CLASS_MEASUREMENT,
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_meta(
                "Frequency grid",
                "frequency_grid",
                None,
                FREQUENCY_HERTZ,
                ICON_FREQ,
                STATE_CLASS_MEASUREMENT,
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_energy_meta(
                "Grid import today",
                "energy_imported",
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_energy_meta(
                "Grid export today",
                "energy_exported",
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_energy_meta(
                "Green Energy today",
                "energy_green",
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_energy_meta(
                "Generated today",
                "energy_generated",
            ),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_power_meta(
                "Power generation",
                "power_generation",
            ),
        )
    )
    totals = coordinator.client.get_power_totals()
    if totals.get(CT_LOAD, None) is not None:
        sensors.append(
            MyenergiHubSensor(
                coordinator,
                entry,
                create_power_meta(
                    "Power charging",
                    "power_charging",
                ),
            )
        )
    if totals.get(CT_BATTERY, None) is not None:
        sensors.append(
            MyenergiHubSensor(
                coordinator,
                entry,
                create_power_meta(
                    "Power battery",
                    "power_battery",
                ),
            )
        )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_power_meta(
                "Home consumption",
                "consumption_home",
            ),
        )
    )
    for device in all_devices:
        # Sensors available in all devices
        sensors.append(
            MyenergiSensor(
                coordinator,
                device,
                entry,
                create_power_meta(
                    f"{device.ct1.name} CT1",
                    "ct1.power",
                ),
            )
        )
        sensors.append(
            MyenergiSensor(
                coordinator,
                device,
                entry,
                create_power_meta(
                    f"{device.ct2.name} CT2",
                    "ct2.power",
                ),
            )
        )
        for key in device.ct_keys:
            sensors.append(MyenergiCTPowerSensor(coordinator, device, entry, key))

        # Sensors common to Zapi and Eddi
        if device.kind in [ZAPPI, EDDI]:
            sensors.append(
                MyenergiSensor(
                    coordinator, device, entry, create_meta("Status", "status")
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_energy_meta("Energy used today", "energy_total"),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_energy_meta("Green energy today", "energy_green"),
                )
            )
            for key in device.ct_keys:
                sensors.append(MyenergiCTEnergySensor(coordinator, device, entry, key))
        # Zappi and harvi
        if device.kind in [ZAPPI, HARVI]:
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_power_meta(
                        f"{device.ct3.name} CT3",
                        "ct3.power",
                    ),
                )
            )
        # Zappi only sensors
        if device.kind == ZAPPI:
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_energy_meta("Charge added session", "charge_added"),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta("Plug status", "plug_status"),
                )
            )

            if device.ct4.name != "None":
                sensors.append(
                    MyenergiSensor(
                        coordinator,
                        device,
                        entry,
                        create_power_meta(
                            f"{device.ct4.name} CT4",
                            "ct4.power",
                        ),
                    )
                )
            if device.ct5.name != "None":
                sensors.append(
                    MyenergiSensor(
                        coordinator,
                        device,
                        entry,
                        create_power_meta(
                            f"{device.ct5.name} CT5",
                            "ct5.power",
                        ),
                    )
                )
            if device.ct6.name != "None":
                sensors.append(
                    MyenergiSensor(
                        coordinator,
                        device,
                        entry,
                        create_power_meta(
                            f"{device.ct6.name} CT6",
                            "ct6.power",
                        ),
                    )
                )
        elif device.kind == EDDI:
            # Eddi specifc sensors
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_energy_meta("Energy consumed session", "consumed_session"),
                )
            )
            if device.temp_1 != -1:
                sensors.append(
                    MyenergiSensor(
                        coordinator,
                        device,
                        entry,
                        create_meta(
                            f"Temp {device.temp_name_1}",
                            "temp_1",
                            DEVICE_CLASS_TEMPERATURE,
                            TEMP_CELSIUS,
                        ),
                    )
                )
            if device.temp_2 != -1:
                sensors.append(
                    MyenergiSensor(
                        coordinator,
                        device,
                        entry,
                        create_meta(
                            f"Temp {device.temp_name_2}",
                            "temp_2",
                            DEVICE_CLASS_TEMPERATURE,
                            TEMP_CELSIUS,
                        ),
                    )
                )
    async_add_devices(sensors)


class MyenergiHubSensor(MyenergiHub, SensorEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, config_entry, meta):
        super().__init__(coordinator, config_entry, meta)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.coordinator.client.serial_number}-{self.meta['prop_name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.coordinator.client.site_name} {self.meta['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        prop_name = self.meta["prop_name"]
        if prop_name == "power_export":
            power = self.coordinator.client.power_grid
            return abs(min(0, power))
        elif prop_name == "power_import":
            power = self.coordinator.client.power_grid
            return max(0, power)
        return operator.attrgetter(prop_name)(self.coordinator.client)

    @property
    def unit_of_measurement(self):
        return self.meta["unit"]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self.meta["icon"]

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return self.meta["device_class"]

    @property
    def state_class(self):
        """Return de device class of the sensor."""
        return self.meta.get("state_class", None)


class MyenergiSensor(MyenergiEntity, SensorEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry, meta):
        super().__init__(coordinator, device, config_entry, meta)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.device.serial_number}-{self.meta['prop_name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} {self.meta['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        value = operator.attrgetter(self.meta["prop_name"])(self.device)
        return value

    @property
    def unit_of_measurement(self):
        return self.meta["unit"]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self.meta["icon"]

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return self.meta["device_class"]

    @property
    def state_class(self):
        """Return de device class of the sensor."""
        return self.meta.get("state_class", None)


class MyenergiCTEnergySensor(MyenergiEntity, SensorEntity):
    """myenergi CT Energy sensor class"""

    def __init__(self, coordinator, device, config_entry, key):
        meta = {
            "name": f"{key.replace('_', ' ')} today",
            "prop_name": key,
            "device_class": DEVICE_CLASS_ENERGY,
            "unit": ENERGY_KILO_WATT_HOUR,
            "state_class": STATE_CLASS_TOTAL_INCREASING,
            "icon": None,
            "attrs": {},
        }
        self.key = key
        super().__init__(coordinator, device, config_entry, meta)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.device.serial_number}-{self.meta['prop_name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} {self.meta['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        value = self.device.history_data.get(self.key, None)
        if value is None:
            return None
        return value

    @property
    def unit_of_measurement(self):
        return self.meta["unit"]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self.meta["icon"]

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return self.meta["device_class"]

    @property
    def state_class(self):
        """Return de device class of the sensor."""
        return self.meta.get("state_class", None)


class MyenergiCTPowerSensor(MyenergiEntity, SensorEntity):
    """myenergi CT power sensor class"""

    def __init__(self, coordinator, device, config_entry, key):
        meta = {
            "name": f"power {key.replace('_', ' ')}",
            "prop_name": f"power-{key}",
            "device_class": DEVICE_CLASS_POWER,
            "state_class": STATE_CLASS_MEASUREMENT,
            "unit": POWER_WATT,
            "icon": None,
            "attrs": {},
        }
        self.key = key
        super().__init__(coordinator, device, config_entry, meta)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.device.serial_number}-{self.meta['prop_name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"myenergi {self.device.name} {self.meta['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.device.ct_groups.get(self.key, None)

    @property
    def unit_of_measurement(self):
        return self.meta["unit"]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self.meta["icon"]

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return self.meta["device_class"]

    @property
    def state_class(self):
        """Return de device class of the sensor."""
        return self.meta.get("state_class", None)
