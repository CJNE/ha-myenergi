"""Sensor platform for myenergi."""

import operator

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.const import UnitOfElectricPotential
from homeassistant.const import UnitOfEnergy
from homeassistant.const import UnitOfFrequency
from homeassistant.const import UnitOfPower
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory
from pymyenergi import CT_BATTERY
from pymyenergi import CT_LOAD
from pymyenergi import EDDI
from pymyenergi import HARVI
from pymyenergi import LIBBI
from pymyenergi import ZAPPI

from .const import DOMAIN
from .entity import MyenergiEntity
from .entity import MyenergiHub

ENTITY_CATEGORY_DIAGNOSTIC = EntityCategory.DIAGNOSTIC

ICON_VOLT = "mdi:lightning-bolt"
ICON_FREQ = "mdi:sine-wave"
ICON_POWER = "mdi:flash"
ICON_HOME_BATTERY = "mdi:home-battery"


def create_meta(
    name,
    prop_name,
    device_class=None,
    unit=None,
    category=None,
    icon=None,
    state_class=None,
):
    """Create metadata for entity"""
    return {
        "name": name,
        "prop_name": prop_name,
        "device_class": device_class,
        "unit": unit,
        "category": category,
        "icon": icon,
        "state_class": state_class,
        "attrs": {},
    }


def create_power_meta(name, prop_name, category=None):
    return {
        "name": name,
        "prop_name": prop_name,
        "device_class": SensorDeviceClass.POWER,
        "unit": UnitOfPower.WATT,
        "category": category,
        "icon": "mdi:flash",
        "state_class": SensorStateClass.MEASUREMENT,
        "attrs": {},
    }


def create_energy_meta(name, prop_name, category=None):
    return {
        "name": name,
        "prop_name": prop_name,
        "device_class": SensorDeviceClass.ENERGY,
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "category": category,
        "icon": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
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
            create_meta("Hub firmware", "firmware_version", icon="mdi:numeric"),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_meta("Hub serial number", "serial_number", icon="mdi:numeric"),
        )
    )
    sensors.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_power_meta(
                "Power grid",
                "power_grid",
                ENTITY_CATEGORY_DIAGNOSTIC,
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
                ENTITY_CATEGORY_DIAGNOSTIC,
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
                ENTITY_CATEGORY_DIAGNOSTIC,
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
                SensorDeviceClass.VOLTAGE,
                UnitOfElectricPotential.VOLT,
                ENTITY_CATEGORY_DIAGNOSTIC,
                ICON_VOLT,
                SensorStateClass.MEASUREMENT,
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
                UnitOfFrequency.HERTZ,
                ENTITY_CATEGORY_DIAGNOSTIC,
                ICON_FREQ,
                SensorStateClass.MEASUREMENT,
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
                ENTITY_CATEGORY_DIAGNOSTIC,
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
                    ENTITY_CATEGORY_DIAGNOSTIC,
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
                    ENTITY_CATEGORY_DIAGNOSTIC,
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
                ENTITY_CATEGORY_DIAGNOSTIC,
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
                create_meta("Firmware", "firmware_version", icon="mdi:numeric"),
            )
        )
        sensors.append(
            MyenergiSensor(
                coordinator,
                device,
                entry,
                create_meta("Serial number", "serial_number", icon="mdi:numeric"),
            )
        )
        sensors.append(
            MyenergiSensor(
                coordinator,
                device,
                entry,
                create_power_meta(
                    f"{device.ct1.name} CT1",
                    "ct1.power",
                    ENTITY_CATEGORY_DIAGNOSTIC,
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
                    ENTITY_CATEGORY_DIAGNOSTIC,
                ),
            )
        )
        for key in device.ct_keys:
            if device.kind == HARVI:
                sensors.append(
                    MyenergiCTPowerSensor(coordinator, device, entry, key, None)
                )
            else:
                sensors.append(
                    MyenergiCTPowerSensor(
                        coordinator, device, entry, key, ENTITY_CATEGORY_DIAGNOSTIC
                    )
                )

        # Sensors common to Zapi and Eddi
        if device.kind in [ZAPPI, EDDI]:
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_energy_meta(
                        "Energy used today", "energy_total", ENTITY_CATEGORY_DIAGNOSTIC
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_energy_meta(
                        "Green energy today", "energy_green", ENTITY_CATEGORY_DIAGNOSTIC
                    ),
                )
            )
            for key in device.ct_keys:
                sensors.append(MyenergiCTEnergySensor(coordinator, device, entry, key))
        # Zappi and harvi
        if device.kind in [ZAPPI, EDDI, HARVI]:
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_power_meta(
                        f"{device.ct3.name} CT3",
                        "ct3.power",
                        ENTITY_CATEGORY_DIAGNOSTIC,
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
                    create_meta(
                        "Number of phases", "num_phases", ENTITY_CATEGORY_DIAGNOSTIC
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta("Status", "status", None, None, None, "mdi:ev-station"),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta("PWM", "pwm", unit=PERCENTAGE),
                )
            )
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
                    create_meta(
                        "Plug status",
                        "plug_status",
                        None,
                        None,
                        None,
                        "mdi:ev-plug-type2",
                    ),
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
                            ENTITY_CATEGORY_DIAGNOSTIC,
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
                            ENTITY_CATEGORY_DIAGNOSTIC,
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
                            ENTITY_CATEGORY_DIAGNOSTIC,
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
                    create_meta("Status", "status", None, None, None, "mdi:shower"),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_energy_meta("Energy consumed session", "consumed_session"),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Active Heater",
                        "active_heater",
                        None,
                        None,
                        None,
                        "mdi:fraction-one-half",
                    ),
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
                            SensorDeviceClass.TEMPERATURE,
                            UnitOfTemperature.CELSIUS,
                            ENTITY_CATEGORY_DIAGNOSTIC,
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
                            SensorDeviceClass.TEMPERATURE,
                            UnitOfTemperature.CELSIUS,
                            ENTITY_CATEGORY_DIAGNOSTIC,
                        ),
                    )
                )
        elif device.kind == LIBBI:
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "SoC",
                        "state_of_charge",
                        SensorDeviceClass.BATTERY,
                        PERCENTAGE,
                        None,
                        None,
                        SensorStateClass.MEASUREMENT,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Voltage",
                        "supply_voltage",
                        SensorDeviceClass.VOLTAGE,
                        UnitOfElectricPotential.VOLT,
                        ENTITY_CATEGORY_DIAGNOSTIC,
                        ICON_VOLT,
                        SensorStateClass.MEASUREMENT,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Frequency",
                        "supply_frequency",
                        None,
                        UnitOfFrequency.HERTZ,
                        ENTITY_CATEGORY_DIAGNOSTIC,
                        ICON_FREQ,
                        SensorStateClass.MEASUREMENT,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Inverter size",
                        "inverter_size",
                        None,
                        UnitOfEnergy.KILO_WATT_HOUR,
                        ENTITY_CATEGORY_DIAGNOSTIC,
                        ICON_POWER,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Battery size",
                        "battery_size",
                        None,
                        UnitOfEnergy.KILO_WATT_HOUR,
                        ENTITY_CATEGORY_DIAGNOSTIC,
                        ICON_POWER,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Status",
                        "status",
                        None,
                        None,
                        None,
                        ICON_HOME_BATTERY,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Grid import today",
                        "grid_import",
                        SensorDeviceClass.ENERGY,
                        UnitOfEnergy.KILO_WATT_HOUR,
                        None,
                        None,
                        SensorStateClass.TOTAL_INCREASING,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Grid export today",
                        "grid_export",
                        SensorDeviceClass.ENERGY,
                        UnitOfEnergy.KILO_WATT_HOUR,
                        None,
                        None,
                        SensorStateClass.TOTAL_INCREASING,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Battery charge today",
                        "battery_charge",
                        SensorDeviceClass.ENERGY,
                        UnitOfEnergy.KILO_WATT_HOUR,
                        None,
                        None,
                        SensorStateClass.TOTAL_INCREASING,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Battery discharge today",
                        "battery_discharge",
                        SensorDeviceClass.ENERGY,
                        UnitOfEnergy.KILO_WATT_HOUR,
                        None,
                        None,
                        SensorStateClass.TOTAL_INCREASING,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Solar generation today",
                        "generated",
                        SensorDeviceClass.ENERGY,
                        UnitOfEnergy.KILO_WATT_HOUR,
                        None,
                        None,
                        SensorStateClass.TOTAL_INCREASING,
                    ),
                )
            )
            sensors.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta(
                        "Charge target",
                        "charge_target",
                        SensorDeviceClass.ENERGY,
                        UnitOfEnergy.KILO_WATT_HOUR,
                        None,
                        None,
                        SensorStateClass.MEASUREMENT,
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
        return f"{self.config_entry.entry_id}-hub-{self.coordinator.client.serial_number}-{self.meta['prop_name']}"

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
        if value is not None:
            return value
        else:
            self._attr_available = False

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
            "device_class": SensorDeviceClass.ENERGY,
            "unit": UnitOfEnergy.KILO_WATT_HOUR,
            "category": ENTITY_CATEGORY_DIAGNOSTIC,
            "state_class": SensorStateClass.TOTAL_INCREASING,
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

    def __init__(self, coordinator, device, config_entry, key, category):
        meta = {
            "name": f"power {key.replace('_', ' ')}",
            "prop_name": f"power-{key}",
            "device_class": SensorDeviceClass.POWER,
            "state_class": SensorStateClass.MEASUREMENT,
            "category": category,
            "unit": UnitOfPower.WATT,
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
