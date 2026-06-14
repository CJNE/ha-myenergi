# Myenergi for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]

[![Community Forum][forum-shield]](https://community.home-assistant.io/t/myenergi-zappi-eddi-harvi/908261)

Myenergi custom component for [Home Assistant](https://home-assistant.io).
This component will make all supported [myenergi](https://myenergi.com) devices connected to your myenergi hub accessible in Home Assistant.
The energy sensors are fully compatible with the energy dashboard in Home Assistant.

It will create HA devices depending on what you have installed:

- Hub

  - Grid power sensor (W)
  - Grid voltage sensor (V)
  - Grid frequency sensor (Hz)
  - Generation power sensor (W)
  - Charging/heating power sensor (W)
  - Home power sensor (W); consumed power that is not charging, heating, generation and export
  - Energy generated today sensor (kWh)
  - Energy exported today sensor (kWh)
  - Energy imported today sensor (kWh)
  - Green energy today sensor (kWh); this is the amount of generated energy that was used for charging or heating instead of being exported

- Zappi

  - Charge mode selector (Stopped, Fast, Eco and Eco+)
  - Phase setting (Automatic, 1 phase, 3 phase); Used in Eco+ charge mode
  - Charge added this session sensor (kWh)
  - Energy consumed today sensor (kWh)
  - Energy diverted today sensor (kWh)
  - Power sensors for internal and external CT clamps (W)
  - Plug status sensor (EV Connected, Waiting for EV, Charging, EV Disconnected)
  - Charger status sensor (Paused, Charging, Boosting, Completed)
  - Minimum green level number input (%); how much power must be sourced from green sources (local generation) to do diversion charging
  - Service to start boost (provide boost amount in kWh as parameter)
  - Service to start smart boost (provide boost amount in kWh and desired finished time as parameters)
  - Service to stop boost
  - Service to unlock the Zappi
  - Sensor for PIN Lock Status (This is not very useful in the real world)
  - Sensor for Charge when Locked Status (This is the sensor that relates to the "unlock" service call and is the one you will want to use)
  - Sensor for lock when plugged in status
  - Sensor for lock when unplugged status

- Eddi

  - Operating mode selector that let you switch between Stopped (no heating will take place) and Normal modes
  - Power sensors for internal and external CT clamps (W)
  - Temperature sensors if fitted
  - Service to start boost (provide boost amount in minutes as parameter)
  - Heater priority; whether the first or second heater should be used first

- Harvi

  - Power sensors for internal and external CT clamps (W)

- Libbi
  - With API Key only
    - Battery discharge today (kWh)
    - Battery size (kW)
    - Frequency (Hz)
    - Grid CT2
    - Grid export today (kWh)
    - Grid import today (kWh)
    - Internal Load CT1
    - Inverter size
    - Operating Mode
    - power ct dcpv (W)
    - power ct internal load (W)
    - SoC (State of Charge) (%)
    - Solar generation today (kWh)
    - Status
    - Voltage (V)
  - With App Credentials (assumed)
    - Battery charge today (kWh)
    - Charge from grid (kWh)
    - Charge target (kWh)

Common sensor entities may also include:

- Serial number
- Firmware version
- Device priority; used for deciding which gets power first

This Home Assistant integration talks to the myenergi API using the [pymyenergi python library](https://github.com/cjne/pymyenergi).

**This component will set up the following platforms.**

| Platform | Description                                         |
| -------- | --------------------------------------------------- |
| `sensor` | Provides various readings for your myenergi devices |
| `select` | Configure devices                                   |
| `number` | Configure devices                                   |

![example][logo]

## HACS Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CJNE&repository=ha-myenergi&category=integration)

1. Search for myenergi in [HACS](https://hacs.xyz/).
2. Install.
3. Restart Home Assistant.

## Configuration

Request an API key from myenergi. You can generate one at your [myenergi account page](https://myaccount.myenergi.com).
See the [myenergi support article](https://support.myenergi.com/hc/en-gb/articles/5069627351185-How-do-I-get-an-API-key-) for more information.

1. Go to `Settings` > `Devices & Services` > `+ Add Integration` button at bottom right 
2. Search for `myenergi` and select it.
3. Enter the Serial numer (`12345678`) and API key.

Ther serial number and API key can both be found under Products at 
[myenergi account page](https://myaccount.myenergi.com)

## Commonly used helpers and automations

### Plugged in (binary sensor)

Helpers > Create Helper > Template > Template a binary sensor

- Name: Zappi Plugged in
- Template: `{{ is_state('sensor.zappi_plug_status', ['Waiting for EV', 'EV Connected', 'Charging']) }}`
- Device class: Plug
- Device: Myenergi Zappi

### Charging (binary sensor)

Helpers > Create Helper > Template > Template a binary sensor

- Name: Charging
- Template: `{{ is_state('sensor.zappi_charger_status', 'Charging') or (
is_state('sensor.zappi_charger_status', 'Boosting') and is_state('binary_sensor.zappi_plugged_in', 'on'))}}`
- Device class: Charging
- Device: Myenergi Zappi

## Troubleshooting

Perform all of the following steps before submitting an issue:

#### Pick up the phone

1. Check the MyEnergi app first to ensure everything works in the MyEnergi eco system.
2. No support can be provided when Octopus is used. Maybe it works, but it can cause unexpected issues which cannot be fixed.

#### Have you tried turning it off and on again?

3. Update the integration to the latest (beta) version
4. Restart Home Assistant.

#### Have you tried forcing an unexpected reboot?

5. Disconnect the Zappi from the car.
6. Force a device reboot: https://support.myenergi.com/hc/en-gb/articles/26093410495121-How-do-I-Reboot-zappi

#### If all else fails

7. Check the (closed) issues and [Community Forum](https://community.home-assistant.io/t/myenergi-zappi-eddi-harvi/908261)

### Updating to the latest (beta) version

go to:

- `HACS` > `Myenergi`.
- from the 3-dot menu, select `Redownload`.
- slecht `Need a different version`.
- Choose the latest (beta) version.

### Updating API key

If you need to change your API key for any reason, you will need to remove the device from "Integration entries", and re-add it again with the new API key.

If the master device is changed or replaced, a new API key is needed.

If an additional device is added, it can take a few hours before it shows up.

This integration is incompatible with Octopus. If Octopus controls your devices, this integration will no longer function correctly.

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md).

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template.

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/cjne.coffee
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/cjne/ha-myenergi.svg?style=for-the-badge
[commits]: https://github.com/cjne/ha-myenergi/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[logo]: logo@2x.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/cjne/ha-myenergi.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40cjne-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/cjne/ha-myenergi.svg?style=for-the-badge
[releases]: https://github.com/cjne/ha-myenergi/releases
[user_profile]: https://github.com/cjne
[myenergi_library]: https://github.com/cjne/pymyenergi
