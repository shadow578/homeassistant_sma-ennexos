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


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class SMADataCoordinator(DataUpdateCoordinator):
    """data coordinator for SMA client."""

    config_entry: ConfigEntry
    data: list[ChannelValues]

    __client: SMAApiClient
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
            update_interval_seconds=config_entry.options.get(
                OPT_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
            ),
        )

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: SMAApiClient,
        update_interval_seconds: int = 60,
    ) -> None:
        """Init."""
        self.__client = client
        self.__all_components = []

        super().__init__(
            hass=hass,
            config_entry=config_entry,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )

    async def _async_setup(self) -> None:
        """Set up the coordinator initially."""
        await self.__client.login()
        self.__all_components = await self.__client.get_all_components()

    async def _async_update_data(self) -> list[ChannelValues]:
        """Update data."""

        try:
            LOGGER.debug("updating data for %s", self.__client.host)

            await self.__client.login()
            measurements = await self.__client.get_live_measurements(query=self.__query)
            # await self.__client.logout()

            return measurements
        except SMAApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except SMAApiCommunicationError as exception:
            raise UpdateFailed(exception) from exception
        except SMAApiParsingError as exception:
            raise UpdateFailed(exception) from exception
        except SMAApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def _async_unload(self) -> None:
        """Unload the coordinator."""
        await self.__client.logout()

    @property
    def all_components(self) -> list[ComponentInfo]:
        """Get all components available."""
        return self.__all_components

    @property
    def __query(self) -> list[LiveMeasurementQueryItem]:
        """Generate measurements query for currently active listeners."""

        # all coordinator sensors set their coordinator context to a
        # tuple (component_id, channel_id) so we can dynamically build
        # the query based on the active listeners only.
        # entities that are disabled are thus not part of the query.
        channels: list[tuple[str, str]] = []
        for _, ctx in self._listeners.values():
            if (
                isinstance(ctx, tuple)
                and len(ctx) == 2
                and isinstance(ctx[0], str)
                and isinstance(ctx[1], str)
            ):
                channels.append(ctx)
            else:
                LOGGER.warning("invalid listener context: '%s'", ctx)

        query = [
            LiveMeasurementQueryItem(component_id=component_id, channel_id=channel_id)
            for component_id, channel_id in channels
        ]

        LOGGER.debug(
            "generated measurements query for %s listeners: %s",
            len(self._listeners),
            ("; ".join([f"{qi.component_id}@{qi.channel_id}" for qi in query])),
        )

        return query
