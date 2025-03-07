"""SMA integration config and options flow."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from attr import dataclass
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_REQUEST_RETIRES,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
    OPT_REQUEST_RETIRES,
    OPT_REQUEST_TIMEOUT,
    OPT_SENSOR_CHANNELS,
    OPT_UPDATE_INTERVAL,
)
from .sma.client import SMAApiClient
from .sma.model import (
    SMAApiAuthenticationError,
    SMAApiClientError,
    SMAApiCommunicationError,
)
from .util import channel_parts_to_fqid


class NoPlantComponentFoundError(Exception):
    """Raised when no plant component is found."""


class SMAConfigFlow(ConfigFlow, domain=DOMAIN):
    """config flow for SMA."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Collect hostname and credentials."""
        _errors = {}
        if user_input is not None:
            # if user enters the hostname with 'http(s)://' or a trailing '/', handle it
            user_input[CONF_HOST] = self.__extract_host(user_input[CONF_HOST])

            try:
                # try to log in using the provided credentials
                plant_name = await self.__fetch_plant_name(
                    host=user_input[CONF_HOST],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    use_ssl=user_input[CONF_USE_SSL],
                    verify_ssl=user_input[CONF_VERIFY_SSL],
                )
            except SMAApiAuthenticationError as exception:
                # credentials not valid
                LOGGER.warning(exception)
                _errors["base"] = "auth_fail"
            except SMAApiCommunicationError as exception:
                # connection error
                LOGGER.error(exception)
                _errors["base"] = "connection_error"
            except NoPlantComponentFoundError as exception:
                # no plant component found, misbehaving api
                LOGGER.error(exception)
                _errors["base"] = "no_plant_component"
            except SMAApiClientError as exception:
                # unknown error
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                # logged in successfully, create config entry
                LOGGER.info("setup successful for plant '%s'", plant_name)
                return self.async_create_entry(
                    title=plant_name,
                    description=f"SMA plant on {user_input[CONF_HOST]}",
                    data=user_input,
                )
        else:
            # for the form, user_input must not be None
            user_input = {}

        # show setup form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    # hostname
                    vol.Required(
                        CONF_HOST, default=user_input.get(CONF_HOST)
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT),
                    ),
                    # username
                    vol.Required(
                        CONF_USERNAME, default=user_input.get(CONF_USERNAME)
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT),
                    ),
                    # password
                    vol.Required(
                        CONF_PASSWORD, default=user_input.get(CONF_PASSWORD)
                    ): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD),
                    ),
                    # use ssl?
                    vol.Required(
                        CONF_USE_SSL, default=user_input.get(CONF_USE_SSL, True)
                    ): BooleanSelector(),
                    # verify ssl?
                    vol.Required(
                        CONF_VERIFY_SSL, default=user_input.get(CONF_VERIFY_SSL, True)
                    ): BooleanSelector(),
                }
            ),
            errors=_errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get options flow handler."""
        return SMAOptionsFlow()

    async def __fetch_plant_name(
        self, host: str, username: str, password: str, use_ssl: bool, verify_ssl: bool
    ) -> str:
        """Login to SMA and get plant name."""
        LOGGER.debug(
            "attempting to get plant name for host=%s and user=%s (use_ssl=%s; verify_ssl=%s)",
            host,
            username,
            use_ssl,
            verify_ssl,
        )
        sma = SMAApiClient(
            host=host,
            username=username,
            password=password,
            session=async_create_clientsession(
                hass=self.hass,
                verify_ssl=verify_ssl,
            ),
            use_ssl=use_ssl,
            request_timeout=DEFAULT_REQUEST_TIMEOUT,
            request_retries=DEFAULT_REQUEST_RETIRES,
            logger=LOGGER.getChild("config_sma_api"),
        )

        await sma.login()
        all_components = await sma.get_all_components()
        await sma.logout()

        # plant name is stored in the first component of type "Plant"
        plant_component = next(
            (
                component
                for component in all_components
                if component.component_type == "Plant"
            ),
            None,
        )
        if plant_component is None:
            raise NoPlantComponentFoundError("No plant component found")

        return plant_component.name

    def __extract_host(self, url_or_host: str) -> str:
        """Extract the host from a input string which is either a url or just a host."""

        # if the input doesn't contain a scheme, add one
        if not url_or_host.startswith(("http://", "https://")):
            url_or_host = "http://" + url_or_host

        # parse the url, return only the host
        parsed_url = urlparse(url_or_host)
        return parsed_url.netloc


@dataclass
class OptionsFlowAvailableChannels:
    """Available channels for selection."""

    component_name: str | None
    component_id: str
    channel_id: str


OPT_ALL_SENSOR_CHANNELS = "use_all_sensor_channels"


class SMAOptionsFlow(OptionsFlow):
    """options flow for SMA."""

    VERSION = 1

    def __init__(self):
        """Initialize options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage enabled sensor channels."""
        # build multi select options
        available_channels = await self.__fetch_available_channels()
        available_channels_opt = {}
        for channel in available_channels:
            fqid = channel_parts_to_fqid(channel.component_id, channel.channel_id)
            available_channels_opt[fqid] = (
                f"{channel.channel_id} @ {channel.component_name}"
            )

        if user_input is not None:
            # apply use_all_channels option
            if user_input.pop(OPT_ALL_SENSOR_CHANNELS, False):
                user_input[OPT_SENSOR_CHANNELS] = list(available_channels_opt.keys())

            return self.async_create_entry(
                data=user_input,
            )

        # show options form
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    # channels
                    vol.Required(
                        OPT_SENSOR_CHANNELS,
                        default=self.config_entry.options.get(OPT_SENSOR_CHANNELS),
                    ): cv.multi_select(available_channels_opt),
                    vol.Required(
                        OPT_ALL_SENSOR_CHANNELS,
                        default=self.config_entry.options.get(
                            OPT_ALL_SENSOR_CHANNELS, False
                        ),
                    ): BooleanSelector(),
                    # refresh interval
                    vol.Required(
                        OPT_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            OPT_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            step=1,
                            unit_of_measurement="s",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    # request timeout
                    vol.Required(
                        OPT_REQUEST_TIMEOUT,
                        default=self.config_entry.options.get(
                            OPT_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=60,
                            step=1,
                            unit_of_measurement="s",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    # request retries
                    vol.Required(
                        OPT_REQUEST_RETIRES,
                        default=self.config_entry.options.get(
                            OPT_REQUEST_RETIRES, DEFAULT_REQUEST_RETIRES
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=0,
                            step=1,
                            unit_of_measurement="",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )

    async def __fetch_available_channels(
        self,
    ) -> list[OptionsFlowAvailableChannels]:
        """Get a list of all available channels and their ids."""
        host = self.config_entry.data[CONF_HOST]
        LOGGER.debug("attempting to fetch available channels for host=%s", host)
        sma = SMAApiClient(
            host=host,
            username=self.config_entry.data[CONF_USERNAME],
            password=self.config_entry.data[CONF_PASSWORD],
            session=async_create_clientsession(
                hass=self.hass,
                verify_ssl=self.config_entry.data[CONF_VERIFY_SSL],
            ),
            use_ssl=self.config_entry.data[CONF_USE_SSL],
            request_timeout=self.config_entry.options.get(
                OPT_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT
            ),
            request_retries=self.config_entry.options.get(
                OPT_REQUEST_RETIRES, DEFAULT_REQUEST_RETIRES
            ),
            logger=LOGGER.getChild("options_sma_api"),
        )

        await sma.login()

        # get components
        all_components = await sma.get_all_components()

        # fetch live data for all components
        all_live_data = await sma.get_all_live_measurements(
            component_ids=[component.component_id for component in all_components]
        )
        await sma.logout()

        # return a dict for each live measurement
        LOGGER.debug("found %s available channels before filtering", len(all_live_data))
        result = [
            OptionsFlowAvailableChannels(
                component_name=next(
                    (
                        component.name
                        for component in all_components
                        if component.component_id == ld.component_id
                    ),
                    None,
                ),
                component_id=ld.component_id,
                channel_id=ld.channel_id,
            )
            for ld in all_live_data
            # ignore all entries that have no value in the latest measurement
            if ld.latest_value.value is not None
        ]
        LOGGER.debug("found %s available channels after filtering", len(result))
        return result
