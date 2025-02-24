# SMA ennexOS for Homeassistant

[![GitHub Release][releases-shield]][releases]
[![codecov](https://codecov.io/github/shadow578/homeassistant_xmltv-epg/graph/badge.svg?token=HGS6DNA4LE)](https://codecov.io/github/shadow578/homeassistant_xmltv-epg)
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]


_Integration to integrate with [SMA ennexOS](sma_ennexos) devices._


## Supported Devices

This integration should work with all SMA ennexOS devices.
These devices are known to be compatible.

- [SMA Data Manager M][sma_data_manager_m]
- [SMA Sunny Tripower X15 and X25](sma_sunny_tripower_x)


## Installation

## HACS (recommended)

1. Add `https://github.com/shadow578/homeassistant_sma-ennexos` as a custom repository, choose `Integration` as Category and add.
2. In the HACS UI, search for `SMA ennexOS` and install it.
3. Restart Home Assistant
4. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "SMA ennexOS"

## Manual

1. Using the tool of choice open the directory for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory there, you need to create it.
2. In the `custom_components` directory create a new folder called `sma_ennexos`.
3. Download _all_ the files from the `custom_components/sma_ennexos/` directory in this repository.
4. Place the files you downloaded in the new directory you created.
5. Restart Home Assistant
6. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "SMA ennexOS"

# Configuration

Configuration is done using the UI.
You'll be prompted to enter the IP and credentials to the SMA ennexOS Device.
After the initial setup, you'll have to configure the channels you want to use in the integration options.
To find available channels, refer to the "Instantaneous Values" menu of the ennexOS web interface.


> [!TIP]
> To Improve reliability, using the installer password is recommended.
> Using the login to the ennexOS Portal works too, but may be less stable as it requires the ennexOS device to maintain a cloud connection.

# Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)


# Notice

This integration is not affiliated with SMA Solar Technology AG in any way.
Use at your own risk.

The SMA, SMA ennexOS, SMA Data Manager and SMA Sunny Tripower X names and logos are trademarks of SMA Solar Technology AG.

***

[sma_ennexos]: https://www.sma.de/produkte/apps-software/ennexos
[sma_data_manager_m]: https://www.sma.de/en/products/monitoring-control/data-manager-m
[sma_sunny_tripower_x]: https://www.sma.de/en/products/solarinverters/sunny-tripower-x
[commits-shield]: https://img.shields.io/github/commit-activity/y/shadow578/homeassistant_sma_data_manager.svg?style=for-the-badge
[commits]: https://github.com/shadow578/homeassistant_sma_data_manager/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/shadow578/homeassistant_sma_data_manager.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40shadow578-blue.svg?style=for-the-badge


[releases-shield]: https://img.shields.io/github/release/shadow578/homeassistant_sma_data_manager.svg?style=for-the-badge
[releases]: https://github.com/shadow578/homeassistant_sma_data_manager/releases
