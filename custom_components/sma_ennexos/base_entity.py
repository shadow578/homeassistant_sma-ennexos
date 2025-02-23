"""base SMA entity class."""

from __future__ import annotations

import uuid

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_MANUFACTURER,
    DOMAIN,
    LOGGER,
)
from .coordinator import SMADataCoordinator
from .sma.model import ComponentInfo


class SMAEntity(CoordinatorEntity):
    """base SMA entity class."""

    def __init__(
        self,
        coordinator: SMADataCoordinator,
        component_id: str,
        channel_id: str,
        component_info: ComponentInfo | None = None,
    ) -> None:
        """Initialize common entity attributes.

        base entity handles device and entity id generation and device info.
        """
        super().__init__(coordinator)

        # generate component (=device) id
        device_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_X500,
                f"{coordinator.config_entry.entry_id}{component_id}",
            )
        )

        # prepare name, serial, and firmware version
        device_name = component_info.name if component_info else f"[{component_id}]"

        device_model_name = (
            None
            if component_info is None or component_info.model_name is None
            else component_info.model_name
        )
        device_serial = (
            None
            if component_info is None or component_info.serial_number is None
            else component_info.serial_number
        )
        device_firmware_version = (
            None
            if component_info is None or component_info.firmware_version is None
            else component_info.firmware_version
        )

        # set device info for the entity
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer=DEVICE_MANUFACTURER,
            model=device_model_name,
            serial_number=device_serial,
            sw_version=device_firmware_version,
        )

        LOGGER.debug(
            "created entity '%s' for channel '%s' of device '%s' (%s)",
            self.entity_id,
            channel_id,
            device_id,
            device_name,
        )
