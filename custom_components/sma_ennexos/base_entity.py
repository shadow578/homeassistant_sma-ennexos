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


class SMAEntity(CoordinatorEntity[SMADataCoordinator]):
    """base SMA entity class."""

    def __init__(
        self,
        coordinator: SMADataCoordinator,
        channel_id: str,
        component_info: ComponentInfo,
    ) -> None:
        """Initialize common entity attributes.

        base entity handles device and entity id generation and device info.
        """
        super().__init__(coordinator, context=(component_info.component_id, channel_id))

        # generate component (=device) id
        device_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_X500,
                f"{coordinator.config_entry.entry_id}{component_info.component_id}",
            )
        )

        # set device info for the entity
        conf_url = (
            f"https://{component_info.ip_address}/"
            if component_info.ip_address
            else None
        )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=component_info.name,
            manufacturer=component_info.vendor or DEVICE_MANUFACTURER,
            model=component_info.product_name,
            serial_number=component_info.serial_number,
            sw_version=component_info.firmware_version,
            configuration_url=conf_url,
        )

        LOGGER.debug(
            "created entity '%s' for channel '%s' of device '%s' (%s)",
            self.entity_id,
            channel_id,
            device_id,
            component_info.name,
        )
