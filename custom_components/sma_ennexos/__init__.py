"""SMA ennexOS integration for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HOST,
    DOMAIN,
    LOGGER,
)
from .coordinator import SMADataCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entry setup."""
    hass.data.setdefault(DOMAIN, {})

    # initialize coordinator, store in hass data entry
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    LOGGER.info(
        "initializing SMA ennexOS integration for host %s", entry.data[CONF_HOST]
    )
    hass.data[DOMAIN][entry.entry_id] = coordinator = (
        SMADataCoordinator.for_config_entry(hass, entry)
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

    # FIXME for some reason, following the example for a coordinated single API poll, the
    # sensors created in sensor.py don't display the data until the next refresh interval.
    # causing a refresh manually after they are set up works around this issue.
    # see https://developers.home-assistant.io/docs/integration_fetching_data/#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_refresh()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of integration entry."""
    LOGGER.info("unloading SMA ennexOS integration")
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        if coordinator is not None and isinstance(coordinator, SMADataCoordinator):
            await coordinator.client.logout()

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
