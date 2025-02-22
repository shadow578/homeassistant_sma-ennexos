"""DataUpdateCoordinator for SMA integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN, LOGGER
from .util import channel_fqid_to_parts, channel_parts_to_fqid

from .sma.client import SMAApiClient
from .sma.model import (
    LiveMeasurementQueryItem,
    ChannelValues,
    SMAApiAuthenticationError,
    SMAApiCommunicationError,
    SMAApiParsingError,
    SMAApiClientError,
)


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class SMAUpdateCoordinator(DataUpdateCoordinator):
    """data update coordinator for SMA client."""

    client: SMAApiClient
    query: list[LiveMeasurementQueryItem]
    data: list[ChannelValues]

    def __init__(
        self,
        hass: HomeAssistant,
        client: SMAApiClient,
        channel_fqids: list[str],
        update_interval_seconds: int = 60,
    ) -> None:
        """Init."""
        self.client = client

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

        # init
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )

    async def _async_update_data(self) -> list[ChannelValues]:
        """Update data."""
        try:
            LOGGER.debug("updating data for %s", self.client.host)

            await self.client.login()
            measurements = await self.client.get_live_measurements(query=self.query)
            #await self.client.logout()

            return measurements
        except SMAApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except SMAApiCommunicationError as exception:
            raise UpdateFailed(exception) from exception
        except SMAApiParsingError as exception:
            raise UpdateFailed(exception) from exception
        except SMAApiClientError as exception:
            raise UpdateFailed(exception) from exception
