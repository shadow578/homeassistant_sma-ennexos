"""SMA integration constants."""

from logging import Logger, getLogger

import homeassistant.const as hass_const

LOGGER: Logger = getLogger(__package__)

DOMAIN = "sma_ennexos"

DEVICE_MANUFACTURER = "SMA"

# configuration keys (config_entry)
CONF_HOST = hass_const.CONF_HOST
CONF_USERNAME = hass_const.CONF_USERNAME
CONF_PASSWORD = hass_const.CONF_PASSWORD
CONF_USE_SSL = hass_const.CONF_SSL
CONF_VERIFY_SSL = hass_const.CONF_VERIFY_SSL

# configuration keys (options)
OPT_REQUEST_TIMEOUT = "request_timeout"
OPT_UPDATE_INTERVAL = "update_interval"
OPT_REQUEST_RETIRES = "request_retries"

# configuration defaults
DEFAULT_REQUEST_TIMEOUT = 10
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_REQUEST_RETIRES = 3
