"""base SMA entity class."""
from __future__ import annotations
import uuid

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    LOGGER,
    DOMAIN,
    DEVICE_MANUFACTURER,
)
from .coordinator import SMAUpdateCoordinator

from .sma.model import ComponentInfo


class SMAEntity(CoordinatorEntity):
    """base SMA entity class."""

    def __init__(
        self,
        coordinator: SMAUpdateCoordinator,
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

        # create entity id from device id and channel id
        self._attr_unique_id = str(
            uuid.uuid5(uuid.NAMESPACE_X500, f"{device_id}{channel_id}")
        )

        # prepare name, serial, and firmware version
        device_name = (
            # fallback to component id
            component_info.name
            if component_info
            else f"[{component_id}]",
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
            model=device_serial,
            sw_version=device_firmware_version,
        )

        LOGGER.debug(
            "created entity '%s' (%s) for channel %s of device '%s' (%s)",
            self.name,
            self.unique_id,
            channel_id,
            device_id,
            device_id,
        )
