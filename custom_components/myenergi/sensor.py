"""Sensor platform for myenergi."""
import operator

from homeassistant.const import DEVICE_CLASS_POWER
from homeassistant.const import POWER_WATT

from .const import DOMAIN
from .entity import MyenergiEntity
from .entity import MyenergiHub


def create_meta(name, prop_name, device_class=None, unit=None, icon=None):
    """Create metadata for entity"""
    return {
        "name": name,
        "prop_name": prop_name,
        "device_class": device_class,
        "unit": unit,
        "icon": icon,
    }


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices = []
    all_devices = await coordinator.client.get_devices()
    devices.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_meta(
                "Power Grid",
                "power_grid",
                DEVICE_CLASS_POWER,
                POWER_WATT,
                "mdi:flash",
            ),
        )
    )
    devices.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_meta(
                "Power Generation",
                "power_generation",
                DEVICE_CLASS_POWER,
                POWER_WATT,
                "mdi:flash",
            ),
        )
    )
    devices.append(
        MyenergiHubSensor(
            coordinator,
            entry,
            create_meta(
                "Home Consumpttion",
                "consumption_home",
                DEVICE_CLASS_POWER,
                POWER_WATT,
                "mdi:flash",
            ),
        )
    )
    for device in all_devices:
        # Sensors available in all devices
        devices.append(
            MyenergiSensor(
                coordinator,
                device,
                entry,
                create_meta(
                    f"{device.ct1.name} CT1",
                    "ct1.power",
                    DEVICE_CLASS_POWER,
                    POWER_WATT,
                    "mdi:flash",
                ),
            )
        )
        devices.append(
            MyenergiSensor(
                coordinator,
                device,
                entry,
                create_meta(
                    f"{device.ct2.name} CT2",
                    "ct2.power",
                    DEVICE_CLASS_POWER,
                    POWER_WATT,
                    "mdi:flash",
                ),
            )
        )
        devices.append(
            MyenergiSensor(
                coordinator,
                device,
                entry,
                create_meta(
                    f"{device.ct3.name} CT3",
                    "ct3.power",
                    DEVICE_CLASS_POWER,
                    POWER_WATT,
                    "mdi:flash",
                ),
            )
        )

        # Sensors common to Zapi and Eddi
        if device.kind in ["zappi", "eddi"]:
            devices.append(
                MyenergiSensor(
                    coordinator, device, entry, create_meta("Status", "status")
                )
            )
        # Zappi only sensors
        if device.kind == "zappi":
            devices.append(
                MyenergiSensor(
                    coordinator,
                    device,
                    entry,
                    create_meta("Plug status", "plug_status"),
                )
            )

            if device.ct4.name != "None":
                devices.append(
                    MyenergiSensor(
                        coordinator,
                        device,
                        entry,
                        create_meta(
                            f"{device.ct4.name} CT4",
                            "ct4.power",
                            DEVICE_CLASS_POWER,
                            POWER_WATT,
                            "mdi:flash",
                        ),
                    )
                )
            if device.ct5.name != "None":
                devices.append(
                    MyenergiSensor(
                        coordinator,
                        device,
                        entry,
                        create_meta(
                            f"{device.ct5.name} CT5",
                            "ct5.power",
                            DEVICE_CLASS_POWER,
                            POWER_WATT,
                            "mdi:flash",
                        ),
                    )
                )
            if device.ct6.name != "None":
                devices.append(
                    MyenergiSensor(
                        coordinator,
                        device,
                        entry,
                        create_meta(
                            f"{device.ct6.name} CT6",
                            "ct6.power",
                            DEVICE_CLASS_POWER,
                            POWER_WATT,
                            "mdi:flash",
                        ),
                    )
                )

    async_add_devices(devices)


class MyenergiHubSensor(MyenergiHub):
    """myenergi Sensor class."""

    def __init__(self, coordinator, config_entry, meta):
        super().__init__(coordinator, config_entry)
        self.meta = meta

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.coordinator.client.serial_number}-{self.meta['prop_name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.coordinator.client.site_name} {self.meta['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return operator.attrgetter(self.meta["prop_name"])(self.coordinator.client)

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


class MyenergiSensor(MyenergiEntity):
    """myenergi Sensor class."""

    def __init__(self, coordinator, device, config_entry, meta):
        super().__init__(coordinator, device, config_entry)
        self.meta = meta

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.device.serial_number}-{self.meta['prop_name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.device.name} {self.meta['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return operator.attrgetter(self.meta["prop_name"])(self.device)

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
