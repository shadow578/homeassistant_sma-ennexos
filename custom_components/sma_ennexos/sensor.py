"""Sensor platform for SMA."""

from __future__ import annotations

import uuid

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_entity import SMAEntity
from .const import DOMAIN, LOGGER
from .coordinator import SMAUpdateCoordinator
from .sma.known_channels import (
    CUMULATIVE_MODE_COUNTER,
    CUMULATIVE_MODE_MAXIMUM,
    CUMULATIVE_MODE_MINIMUM,
    CUMULATIVE_MODE_NONE,
    CUMULATIVE_MODE_TOTAL,
    DEVICE_KIND_BATTERY,
    DEVICE_KIND_GRID,
    DEVICE_KIND_PV,
    UNIT_AMPERE,
    UNIT_CELSIUS,
    UNIT_ENUM,
    UNIT_HERTZ,
    UNIT_PERCENT,
    UNIT_SECOND,
    UNIT_VOLT,
    UNIT_VOLT_AMPERE_REACTIVE,
    UNIT_WATT,
    UNIT_WATT_HOUR,
    get_known_channel,
)
from .sma.model import ComponentInfo
from .util import SMAEntryData, channel_parts_to_entity_id, channel_parts_to_fqid


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Sensor entities setup."""
    entry_data: SMAEntryData = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry_data.coordinator
    all_components = entry_data.all_components

    # ensure that coordinator and all_components are available
    if coordinator is None or all_components is None:
        LOGGER.error(
            "cannot create sensor entities for config entry %s: coordinator or all_components not available",
            config_entry.entry_id,
        )
        return

    # ensure coordinator.config_entry is set
    if coordinator.config_entry is None:
        LOGGER.warning("coordinator.config_entry was None, setting to config_entry")
        coordinator.config_entry = config_entry

    # create entities based on ChannelValues in coordinator.data
    LOGGER.info("creating %s sensor entities", len(coordinator.data))
    async_add_entities(
        [
            SMASensor(
                coordinator=coordinator,
                component_id=channel_value.component_id,
                channel_id=channel_value.channel_id,
                component_info=next(
                    comp
                    for comp in all_components
                    if comp.component_id == channel_value.component_id
                )
                or None,
            )
            for channel_value in coordinator.data
        ]
    )


class SMASensor(SMAEntity, SensorEntity):
    """SMA Sensor class."""

    coordinator: SMAUpdateCoordinator
    component_id: str
    channel_id: str

    enum_values: dict[int, str] | None = None

    def __init__(
        self,
        coordinator: SMAUpdateCoordinator,
        component_id: str,
        channel_id: str,
        component_info: ComponentInfo | None = None,
    ) -> None:
        """Initialize SMA sensor."""
        self.component_id = component_id
        self.channel_id = channel_id

        # create entity id from device id and channel id
        self.entity_id = channel_parts_to_entity_id(component_id, channel_id, "sensor")
        self._attr_unique_id = str(uuid.uuid5(uuid.NAMESPACE_X500, self.entity_id))

        # super handles setting id and device_info for us
        super().__init__(
            coordinator=coordinator,
            component_id=component_id,
            channel_id=channel_id,
            component_info=component_info,
        )
        self.__set_description()

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        data = self.coordinator.data

        # find the ChannelValues of this sensor
        channel_values = next(
            ch_val
            for ch_val in data
            if ch_val.component_id == self.component_id
            and ch_val.channel_id == self.channel_id
        )

        # get latest value
        value = channel_values.latest_value().value

        # handle enum value translation to string
        if self.enum_values is not None:
            # enum values are always ints
            # fallback to raw value if no enum value found or invalid
            if isinstance(value, int):
                value = self.enum_values.get(value, f"[{value}]")
            else:
                LOGGER.warning(
                    "enum_values set, but value is not an int: %s (%s)",
                    value,
                    type(value),
                )
                value = f"[{value}]"

        # return value
        LOGGER.debug("updated %s = %s (%s)", self.entity_id, value, type(value))
        return value

    def __set_description(self) -> None:
        """Set entity description using known channels."""
        fqid = channel_parts_to_fqid(self.component_id, self.channel_id)

        # get entry for known channel
        known_channel = get_known_channel(self.channel_id)

        # values set by known channel unit
        name = self.channel_id
        icon = None
        device_class = None
        unit_of_measurement = None
        state_class = SensorStateClass.MEASUREMENT
        if known_channel is not None:
            name = known_channel.name

            icon = self.__device_kind_to_icon(known_channel.device_kind)

            (device_class, unit_of_measurement) = (
                self.__channel_to_device_class_and_unit(
                    self.channel_id, known_channel.unit
                )
            )

            cumulative_mode = known_channel.cumulative_mode
            state_class = self.__cumulative_mode_to_state_class(
                cumulative_mode if cumulative_mode is not None else CUMULATIVE_MODE_NONE
            )

            # set enum_values if known channel is UNIT_ENUM
            if known_channel.unit == UNIT_ENUM:
                self.enum_values = known_channel.enum_values
                if self.enum_values is None:
                    LOGGER.warning(
                        "UNIT_ENUM set, but enum_values is None: %s", self.channel_id
                    )
                    self.enum_values = {}

            # device class ENUM requires state class to be None
            if device_class == SensorDeviceClass.ENUM:
                state_class = None

            LOGGER.debug(
                "configure %s using known channel:"
                "name=%s; icon=%s, device_class=%s, unit_of_measurement=%s, state_class=%s",
                fqid,
                name,
                icon,
                device_class,
                unit_of_measurement,
                state_class,
            )
        else:
            LOGGER.debug("configure %s as generic sensor", fqid)

        # set entity description
        self.entity_description = SensorEntityDescription(
            key=fqid,
            name=name,
            icon=icon,
            device_class=device_class,
            native_unit_of_measurement=unit_of_measurement,
            state_class=state_class,
        )

    def __device_kind_to_icon(self, device_kind: str) -> str:
        """SMA DEVICE_KIND_* to mdi icon."""
        if device_kind == DEVICE_KIND_GRID:
            return "mdi:transmission-tower"
        if device_kind == DEVICE_KIND_BATTERY:
            return "mdi:battery"
        if device_kind == DEVICE_KIND_PV:
            return "mdi:solar-panel"

        # DEVICE_KIND_OTHER
        return "mdi:flash"

    def __channel_to_device_class_and_unit(
        self, channel_id: str, channel_unit: str
    ) -> tuple[SensorDeviceClass | None, str | None]:
        """SMA UNIT_* to device_class and unit_of_measurement.

        :return: (device_class, unit_of_measurement):
            device_class is None for where no device_class is available
            unit_of_measurement is None for plain numbers without unit
        """
        # special handling:
        if channel_id == "Measurement.Bat.ChaStt":
            # battery SoC has its own device class
            return (SensorDeviceClass.BATTERY, PERCENTAGE)
        if channel_id == "Measurement.Bat.Diag.StatTm":
            # battery operating time is overwritten to device class DURATION
            return (SensorDeviceClass.DURATION, UnitOfTime.SECONDS)

        # handle by channel unit
        if channel_unit == UNIT_VOLT:
            return (SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT)
        if channel_unit == UNIT_AMPERE:
            return (SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE)
        if channel_unit == UNIT_WATT:
            return (SensorDeviceClass.POWER, UnitOfPower.WATT)
        if channel_unit == UNIT_WATT_HOUR:
            return (SensorDeviceClass.ENERGY, UnitOfEnergy.WATT_HOUR)
        if channel_unit == UNIT_CELSIUS:
            return (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS)
        if channel_unit == UNIT_HERTZ:
            return (SensorDeviceClass.FREQUENCY, UnitOfFrequency.HERTZ)
        if channel_unit == UNIT_VOLT_AMPERE_REACTIVE:
            return (
                SensorDeviceClass.REACTIVE_POWER,
                UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            )
        if channel_unit == UNIT_SECOND:
            return (None, UnitOfTime.SECONDS)
        if channel_unit == UNIT_PERCENT:
            return (None, PERCENTAGE)
        if channel_unit == UNIT_ENUM:
            return (SensorDeviceClass.ENUM, None)

        # fallback to PLAIN_NUMBER
        return (None, None)

    def __cumulative_mode_to_state_class(self, cumulative_mode: str) -> str:
        """SMA CUMULATIVE_MODE_* to SensorStateClass."""

        # counters only ever increase
        if cumulative_mode == CUMULATIVE_MODE_COUNTER:
            return SensorStateClass.TOTAL_INCREASING

        # total only ever increases
        if cumulative_mode == CUMULATIVE_MODE_TOTAL:
            return SensorStateClass.TOTAL_INCREASING

        # min / max are modeled as TOTAL, since minimum can decrease
        if cumulative_mode == CUMULATIVE_MODE_MINIMUM:
            return SensorStateClass.TOTAL
        if cumulative_mode == CUMULATIVE_MODE_MAXIMUM:
            return SensorStateClass.TOTAL

        # default to CUMULATIVE_MODE_NONE
        return SensorStateClass.MEASUREMENT
