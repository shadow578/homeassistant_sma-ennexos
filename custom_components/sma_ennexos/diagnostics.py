"""Diagnostics for SMA ennexOS integration."""

from __future__ import annotations

from dataclasses import asdict

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry

from custom_components.sma_ennexos.coordinator import SMADataCoordinator

from .const import CONF_PASSWORD, CONF_USERNAME

TO_REDACT = {
    # config entry
    CONF_USERNAME,
    CONF_PASSWORD,
    # component info
    "serial_number",
}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    """Return diagnostics for the config entry."""
    # get config entry data
    config_entry = entry.as_dict()
    if "data" in config_entry:
        config_entry["data"] = async_redact_data(config_entry["data"], TO_REDACT)

    # get active entities
    er = entity_registry.async_get(hass)
    entity_ids = [
        entity.entity_id
        for entity in entity_registry.async_entries_for_config_entry(er, entry.entry_id)
    ]
    entity_states = {entity: hass.states.get(entity) for entity in entity_ids}

    # get all components and measurements info
    api_raw_data: dict = {}
    coordinator = hass.data["sma_ennexos"][entry.entry_id]
    if isinstance(coordinator, SMADataCoordinator):
        components = [
            async_redact_data(asdict(component), TO_REDACT)
            for component in coordinator.all_components
        ]
        measurements = [
            async_redact_data(asdict(measurement), TO_REDACT)
            for measurement in coordinator.all_measurements
        ]

        localizations = []
        try:
            locs = await coordinator.client.get_localizations()
            for filename, lang_data in locs:
                redacted_lang_data = async_redact_data(lang_data, TO_REDACT)
                localizations.append(
                    {"filename": filename, "lang_data": redacted_lang_data}
                )
        except Exception as e:
            localizations.append({"error": f"Failed to get localizations: {e}"})

        api_raw_data = {
            "components": components,
            "measurements": measurements,
            "localizations": localizations,
        }

    return {
        "config_entry": config_entry,
        "entities": entity_states,
        "raw_data": api_raw_data,
    }
