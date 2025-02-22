"""SMA Data Manager M integration for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
from .coordinator import SMAUpdateCoordinator
from .sma.client import SMAApiClient
from .util import SMAEntryData

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entry setup."""
    hass.data.setdefault(DOMAIN, {})

    # initialize SMA client
    LOGGER.info(
        "initializing SMA data manager integration for host %s", entry.data[CONF_HOST]
    )
    client = SMAApiClient(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        session=async_get_clientsession(
            hass=hass, verify_ssl=entry.data[CONF_VERIFY_SSL]
        ),
        use_ssl=entry.data[CONF_USE_SSL],
        request_timeout=entry.options.get(OPT_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT),
        request_retries=entry.options.get(OPT_REQUEST_RETIRES, DEFAULT_REQUEST_RETIRES),
        logger=LOGGER,
    )

    # get component info from SMA client once
    await client.login()
    all_components = await client.get_all_components()
    # await client.logout()

    # initialize coordinator
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    coordinator = SMAUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=client,
        channel_fqids=entry.options.get(OPT_SENSOR_CHANNELS, []),
        update_interval_seconds=entry.options.get(
            OPT_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
        ),
    )

    # store coordinator in hass data
    hass.data[DOMAIN][entry.entry_id] = SMAEntryData(
        coordinator=coordinator,
        all_components=all_components,
    )

    if entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
        # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
        await coordinator.async_config_entry_first_refresh()
    else:
        # To fix deprecation warning (???)
        # Detected that custom integration 'xmltv_epg' uses `async_config_entry_first_refresh`, which is only supported when entry state is ConfigEntryState.SETUP_IN_PROGRESS, but it is in state ConfigEntryState.LOADED
        await coordinator.async_refresh()

    # setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of integration entry."""
    LOGGER.info("unloading SMA data manager integration")
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry_data = hass.data[DOMAIN].pop(entry.entry_id)
        if entry_data is not None and isinstance(entry_data, SMAEntryData):
            await entry_data.coordinator.client.logout()

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
