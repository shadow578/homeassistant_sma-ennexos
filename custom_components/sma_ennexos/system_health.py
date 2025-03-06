"""Provide info to system health."""

from typing import Any
from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from custom_components.sma_ennexos.const import DOMAIN
from custom_components.sma_ennexos.coordinator import SMADataCoordinator


@callback
def async_register(
    hass: HomeAssistant, register: system_health.SystemHealthRegistration
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)

async def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Get info for the info page."""
    config_entry = hass.config_entries.async_entries(DOMAIN)[0]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    if not isinstance(coordinator, SMADataCoordinator):
        return {}

    return {
        "host": coordinator.client.host
    }
