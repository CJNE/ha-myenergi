# MyEnergi for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

MyEnergi custom component for [Home Assistant](https://home-assistant.io).
This component will make all supported [MyEnergi](https://myenergi.com) devices (libbi is not currently supported) connected to your MyEnergi hub accessible in Home Assistant.
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
  - Minumum green level number input (%); how much power must be sourced from green sources (local generation) to do diversion charging
  - Service to start boost (provide boost amount in kWh as parameter)
  - Service to start smart boost (provide boost amount in kWh and desired finished time as paramters)
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

Common sensor entities may also include:

- Serial number
- Firmware version
- Device priority; used for deciding which gets power first

This Home Assistant integration talks to the MyEnergi API using the [pymyenergi python library](https://github.com/cjne/pymyenergi).

**This component will set up the following platforms.**

| Platform | Description                                         |
| -------- | --------------------------------------------------- |
| `sensor` | Provides various readings for your myenergi devices |
| `select` | Configure devices                                   |
| `number` | Configure devices                                   |

![example][logo]

## HACS Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CJNE&repository=ha-myenergi&category=integration)

This is the recommended way to install.

1. Search for myenergi in [HACS](https://hacs.xyz/).
2. Install.
3. Restart Home Assistant.
4. In the HA UI, click Settings in the left nav bar, then click "Devices & Services". By default you should be viewing the Integrations tab. Click "+ Add Integration" button at bottom right and then search for "myenergi".

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `myenergi`.
4. Download _all_ the files from the `custom_components/myenergi/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant.
7. In the HA UI, click Settings in the left nav bar, then click "Devices & Services". By default you should be viewing the Integrations tab. Click "+ Add Integration" button at bottom right and then search for "myenergi".

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/myenergi/translations/en.json
custom_components/myenergi/translations/fr.json
custom_components/myenergi/translations/sv.json
custom_components/myenergi/translations/nb.json
custom_components/myenergi/__init__.py
custom_components/myenergi/config_flow.py
custom_components/myenergi/const.py
custom_components/myenergi/entity.py
custom_components/myenergi/manifest.json
custom_components/myenergi/number.py
custom_components/myenergi/select.py
custom_components/myenergi/sensor.py
custom_components/myenergi/services.yaml
```

## Configuration is done in the UI

If you have trouble logging in you might need to request an API key from myenergi. You can generate one at your [myenergi account page](https://myaccount.myenergi.com).
See the [myenergi support article](https://support.myenergi.com/hc/en-gb/articles/5069627351185-How-do-I-get-an-API-key-) for more information.

## Troubleshooting

in case of issues, check the MyEnergi app first to ensure everything works in the MyEnergi eco system.

If you need to change your API key for any reason, you will need to remove the device from "Integration entries", and re-add it again with the new API key.

If the master device is changed or replaced, a new API key is needed.

If an additional device is added, it can take a few hours before it shows up.

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
