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
from .coordinator import SMADataCoordinator
from .sma.known_channels import (
    SMACumulativeMode,
    SMADeviceKind,
    SMAUnit,
    get_known_channel,
)
from .sma.model import ComponentInfo
from .util import (
    channel_parts_to_entity_id,
    channel_parts_to_fqid,
    channel_to_translation_key,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Sensor entities setup."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    if not isinstance(coordinator, SMADataCoordinator):
        LOGGER.error(
            "cannot create sensor entities for config entry %s: coordinator is not SMADataCoordinator",
            config_entry.entry_id,
        )
        return

    all_components = await coordinator.get_all_components()

    # create entities based on ChannelValues in coordinator.data
    LOGGER.info("creating %s sensor entities", len(coordinator.data))
    async_add_entities(
        [
            SMASensor(
                coordinator=coordinator,
                channel_id=channel_value.channel_id,
                component_info=next(
                    comp
                    for comp in all_components
                    if comp.component_id == channel_value.component_id
                ),
            )
            for channel_value in coordinator.data
        ]
    )


class SMASensor(SMAEntity, SensorEntity):
    """SMA Sensor class."""

    coordinator: SMADataCoordinator
    component_id: str
    channel_id: str

    enum_values: dict[int, str] | None = None

    def __init__(
        self,
        coordinator: SMADataCoordinator,
        channel_id: str,
        component_info: ComponentInfo,
    ) -> None:
        """Initialize SMA sensor."""
        self.component_id = component_info.component_id
        self.channel_id = channel_id

        # create entity id from device id and channel id
        self.entity_id = channel_parts_to_entity_id(
            component_info.name if component_info is not None else self.component_id,
            channel_id,
            "sensor",
        )
        self._attr_unique_id = str(uuid.uuid5(uuid.NAMESPACE_X500, self.entity_id))

        # super handles setting id and device_info for us
        super().__init__(
            coordinator=coordinator,
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
        value = channel_values.latest_value.value

        # check for fallback value in known_channels for None
        if value is None:
            known_channel = get_known_channel(self.channel_id)
            if known_channel is not None:
                value = known_channel.value_when_none

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
        icon = None
        device_class = None
        unit_of_measurement = None
        state_class = SensorStateClass.MEASUREMENT
        suggested_display_precision = None
        if known_channel is not None:
            icon = self.__device_kind_to_icon(known_channel.device_kind)

            (device_class, unit_of_measurement) = (
                self.__channel_to_device_class_and_unit(
                    self.channel_id, known_channel.unit
                )
            )

            state_class = self.__cumulative_mode_to_state_class(
                known_channel.cumulative_mode
            )

            suggested_display_precision = self.__unit_to_display_precision(
                known_channel.unit
            )

            # set enum_values if known channel is UNIT_ENUM
            if known_channel.unit == SMAUnit.ENUM:
                self.enum_values = known_channel.enum_values
                if self.enum_values is None:
                    LOGGER.warning(
                        "unit ENUM set, but enum_values is None: %s", self.channel_id
                    )
                    self.enum_values = {}

            # device class ENUM requires state class to be None
            if device_class == SensorDeviceClass.ENUM:
                state_class = None

            LOGGER.debug(
                "configure %s using known channel:"
                "icon=%s, device_class=%s, unit_of_measurement=%s, state_class=%s, suggested_display_precision=%s",
                fqid,
                icon,
                device_class,
                unit_of_measurement,
                state_class,
                suggested_display_precision,
            )
        else:
            LOGGER.debug("configure %s as generic sensor", fqid)

        # assume all channels in known_channels have a translation.
        # if a sensor is setup with a translation key that does not exist, the UI will show 'None'.
        # this setup makes it so any known channel will show with a nice translation, and any
        # unknown channel will show the SMA channel id as its name, with the option for the user to rename it.
        has_translation_key = known_channel is not None
        translation_key = channel_to_translation_key(self.channel_id)

        self.entity_description = SensorEntityDescription(
            key=translation_key,
            translation_key=translation_key if has_translation_key else None,
            name=self.channel_id if not has_translation_key else None,
            icon=icon,
            device_class=device_class,
            native_unit_of_measurement=unit_of_measurement,
            state_class=state_class,
            suggested_display_precision=suggested_display_precision,
        )

        # required for using translation_key
        self._attr_has_entity_name = has_translation_key

    def __device_kind_to_icon(self, device_kind: SMADeviceKind) -> str:
        """SMADeviceKind to mdi icon."""
        if device_kind == SMADeviceKind.GRID:
            return "mdi:transmission-tower"
        if device_kind == SMADeviceKind.BATTERY:
            return "mdi:battery"
        if device_kind == SMADeviceKind.PV:
            return "mdi:solar-panel"

        # SMADeviceKind.OTHER
        return "mdi:flash"

    def __channel_to_device_class_and_unit(
        self, channel_id: str, channel_unit: SMAUnit
    ) -> tuple[SensorDeviceClass | None, str | None]:
        """SMAUnit to device_class and unit_of_measurement.

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
        if channel_unit == SMAUnit.VOLT:
            return (SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT)
        if channel_unit == SMAUnit.AMPERE:
            return (SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE)
        if channel_unit == SMAUnit.WATT:
            return (SensorDeviceClass.POWER, UnitOfPower.WATT)
        if channel_unit == SMAUnit.WATT_HOUR:
            return (SensorDeviceClass.ENERGY, UnitOfEnergy.WATT_HOUR)
        if channel_unit == SMAUnit.CELSIUS:
            return (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS)
        if channel_unit == SMAUnit.HERTZ:
            return (SensorDeviceClass.FREQUENCY, UnitOfFrequency.HERTZ)
        if channel_unit == SMAUnit.VOLT_AMPERE_REACTIVE:
            return (
                SensorDeviceClass.REACTIVE_POWER,
                UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            )
        if channel_unit == SMAUnit.SECONDS:
            return (None, UnitOfTime.SECONDS)
        if channel_unit == SMAUnit.PERCENT:
            return (None, PERCENTAGE)
        if channel_unit == SMAUnit.ENUM:
            return (SensorDeviceClass.ENUM, None)

        # fallback to PLAIN_NUMBER
        return (None, None)

    def __cumulative_mode_to_state_class(
        self, cumulative_mode: SMACumulativeMode | None
    ) -> str:
        """SMACumulativeMode to SensorStateClass."""

        # counters only ever increase
        if cumulative_mode == SMACumulativeMode.COUNTER:
            return SensorStateClass.TOTAL_INCREASING

        # total only ever increases
        if cumulative_mode == SMACumulativeMode.TOTAL:
            return SensorStateClass.TOTAL_INCREASING

        # min / max are modeled as TOTAL, since minimum can decrease
        if cumulative_mode == SMACumulativeMode.MINIMUM:
            return SensorStateClass.TOTAL
        if cumulative_mode == SMACumulativeMode.MAXIMUM:
            return SensorStateClass.TOTAL

        return SensorStateClass.MEASUREMENT

    def __unit_to_display_precision(self, unit: SMAUnit) -> int | None:
        """SMAUnit to display precision."""

        if (
            unit == SMAUnit.VOLT
            or unit == SMAUnit.AMPERE
            or unit == SMAUnit.WATT
            or unit == SMAUnit.WATT_HOUR
            or unit == SMAUnit.HERTZ
            or unit == SMAUnit.VOLT_AMPERE_REACTIVE
            or unit == SMAUnit.SECONDS
        ):
            # display no decimal places
            return 0

        if unit == SMAUnit.CELSIUS:
            # display one decimal place
            return 1

        if unit == SMAUnit.PERCENT:
            # display two decimal places
            return 2

        # PLAIN_NUMBER or ENUM
        return None
