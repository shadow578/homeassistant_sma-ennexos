"""DataUpdateCoordinator for SMA integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
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
    ChannelValues,
    ComponentInfo,
    LiveMeasurementQueryItem,
    SMAApiAuthenticationError,
    SMAApiClientError,
    SMAApiCommunicationError,
    SMAApiParsingError,
)
from .util import channel_fqid_to_parts, channel_parts_to_fqid


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class SMADataCoordinator(DataUpdateCoordinator):
    """data coordinator for SMA client."""

    config_entry: ConfigEntry

    client: SMAApiClient
    query: list[LiveMeasurementQueryItem]
    data: list[ChannelValues]

    __all_components: list[ComponentInfo]

    @classmethod
    def for_config_entry(
        cls,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> SMADataCoordinator:
        """Create a new instance of the coordinator given a config entry."""
        client = SMAApiClient(
            host=config_entry.data[CONF_HOST],
            username=config_entry.data[CONF_USERNAME],
            password=config_entry.data[CONF_PASSWORD],
            session=async_get_clientsession(
                hass=hass, verify_ssl=config_entry.data[CONF_VERIFY_SSL]
            ),
            use_ssl=config_entry.data[CONF_USE_SSL],
            request_timeout=config_entry.options.get(
                OPT_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT
            ),
            request_retries=config_entry.options.get(
                OPT_REQUEST_RETIRES, DEFAULT_REQUEST_RETIRES
            ),
            logger=LOGGER,
        )

        return SMADataCoordinator(
            hass=hass,
            config_entry=config_entry,
            client=client,
            channel_fqids=config_entry.options.get(OPT_SENSOR_CHANNELS, []),
            update_interval_seconds=config_entry.options.get(
                OPT_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
            ),
        )

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: SMAApiClient,
        channel_fqids: list[str],
        update_interval_seconds: int = 60,
    ) -> None:
        """Init."""
        self.client = client
        self.__all_components = []

        # prepare query
        self.query = []
        for fqid in channel_fqids:
            (component_id, channel_id) = channel_fqid_to_parts(fqid)
            self.query.append(
                LiveMeasurementQueryItem(
                    component_id=component_id, channel_id=channel_id
                )
            )

        LOGGER.debug(
            "setup coordinator with query: %s",
            (
                "; ".join(
                    [
                        channel_parts_to_fqid(qi.component_id, qi.channel_id)
                        for qi in self.query
                    ]
                )
            ),
        )

        super().__init__(
            hass=hass,
            config_entry=config_entry,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )

    async def _async_setup(self) -> None:
        """Set up the coordinator initially."""
        await self.client.login()
        self.__all_components = await self.client.get_all_components()

    async def _async_update_data(self) -> list[ChannelValues]:
        """Update data."""
        try:
            LOGGER.debug("updating data for %s", self.client.host)

            await self.client.login()
            measurements = await self.client.get_live_measurements(query=self.query)
            # await self.client.logout()

            return measurements
        except SMAApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except SMAApiCommunicationError as exception:
            raise UpdateFailed(exception) from exception
        except SMAApiParsingError as exception:
            raise UpdateFailed(exception) from exception
        except SMAApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def get_all_components(self) -> list[ComponentInfo]:
        """Get all available components from the API."""
        return self.__all_components
