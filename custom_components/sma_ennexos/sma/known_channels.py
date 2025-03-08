"""SMA known channels."""

from enum import Enum

from attr import dataclass

from custom_components.sma_ennexos.sma.model import SMAValue


class SMAUnit(str, Enum):
    """SMA known channel units."""

    # a generic, plain number
    PLAIN_NUMBER = "plain_number"
    VOLT = "volt"
    AMPERE = "ampere"
    WATT = "watt"
    WATT_HOUR = "watt_hour"
    CELSIUS = "celsius"
    HERTZ = "hertz"
    VOLT_AMPERE_REACTIVE = "volt_ampere_reactive"
    SECONDS = "seconds"
    PERCENT = "percent"

    # SMA enum, value keys defined in KnownChannel enum_values dict
    ENUM = "enum"


class SMADeviceKind(str, Enum):
    """SMA known channel device kinds."""

    GRID = "GRID"
    BATTERY = "BATTERY"
    PV = "PV"
    OTHER = "OTHER"


class SMACumulativeMode(str, Enum):
    """SMA known channel cumulative modes."""

    # increasing counter value, e.g. error count, operating time
    COUNTER = "COUNTER"

    # total value, e.g. pv yield
    TOTAL = "TOTAL"

    # minimum measurement, e.g. minimum temperature
    MINIMUM = "MINIMUM"

    # maximum measurement, e.g. maximum temperature
    MAXIMUM = "MAXIMUM"


class SMAChannelCategory(str, Enum):
    """SMA known channel categories."""

    # a operational value, e.g. inverter power
    OPERATIONAL = "OPERATIONAL"

    # a diagnostic value, e.g. temperature, status or error count
    DIAGNOSTIC = "DIAGNOSTIC"


__CONNECTION_STATUS_ENUM_VALUES = {
    55: "communication_error",
    303: "off",
    307: "ok",
    455: "warning",
}

__COMMON_ENUM_VALUES = {
    **__CONNECTION_STATUS_ENUM_VALUES,
    304: "island_operation",
    305: "island_operation",
    306: "island_operation",
    308: "on",
    309: "operating",
    311: "open",
    312: "phase_assignment",
    313: "island_operation",
    314: "maximum_active_power",
    315: "maximum_active_power_output",
    316: "active_power_setpoint_operating_mode",
    318: "overload",
    319: "overtemperature",
    454: "calibration",
    456: "waiting_for_dc_start_condition",
    457: "waiting_for_grid_voltage",
}


@dataclass
class KnownChannelEntry:
    """Entry in the __KNOWN_CHANNELS dict."""

    # kind of device this channel belongs to
    device_kind: SMADeviceKind

    # unit of the channel value
    unit: SMAUnit

    # optional cumulative mode
    cumulative_mode: SMACumulativeMode | None = None

    # optional category of the channel
    category: SMAChannelCategory = SMAChannelCategory.OPERATIONAL

    # optional list of enum values, only with unit=SMAUnit.ENUM
    enum_values: dict[int, str] | None = None

    # optional value when the channel is not available.
    # for enum values, this is the numeric index
    value_when_none: SMAValue | None = None


__KNOWN_CHANNELS: dict[
    str,
    KnownChannelEntry,
] = {
    "Measurement.GridMs.TotVAr": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.GridMs.TotVAr.Pv": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.GridMs.TotW": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.GridMs.TotW.Pv": KnownChannelEntry(
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Inverter.CurWCtlNom": KnownChannelEntry(
        device_kind=SMADeviceKind.PV, unit=SMAUnit.PERCENT
    ),
    "Measurement.Inverter.WAval": KnownChannelEntry(
        device_kind=SMADeviceKind.PV, unit=SMAUnit.WATT
    ),
    "Measurement.Metering.GridMs.TotWIn.Bat": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Metering.GridMs.TotWOut.Bat": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Metering.GridMs.TotWhIn.Bat": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.GridMs.TotWhOut.Bat": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.PCCMs.PlntA.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.Metering.PCCMs.PlntA.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.Metering.PCCMs.PlntA.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.Metering.PCCMs.PlntCsmpW": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.WATT
    ),
    "Measurement.Metering.PCCMs.PlntCsmpWh": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.PCCMs.PlntPF": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,  # TODO Measurement.Metering.PCCMs.PlntPF unit is not validated
    ),
    "Measurement.Metering.PCCMs.PlntPhV.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.Metering.PCCMs.PlntPhV.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.Metering.PCCMs.PlntPhV.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.Metering.PCCMs.PlntVAr": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.PCCMs.PlntVAr.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.PCCMs.PlntVAr.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.PCCMs.PlntVAr.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.PCCMs.PlntW": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.Metering.PCCMs.PlntW.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.Metering.PCCMs.PlntW.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.Metering.PCCMs.PlntW.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.Metering.PCCMs.PlntWh": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.TotWhOut.Pv": KnownChannelEntry(
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Operation.CurAvailPlnt": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.PERCENT,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Operation.CurAvailVArOvExt": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Operation.CurAvailVArOvExtNom": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.CurAvailVArUnExt": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Operation.CurAvailVArUnExtNom": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.Health": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.ENUM,
        category=SMAChannelCategory.DIAGNOSTIC,
        enum_values=__COMMON_ENUM_VALUES,  # TODO: Measurement.Operation.Health enum_values may be partially incorrect, only [55, 307, 455] are validated
    ),
    "Measurement.Operation.WMaxInLimNom": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.WMaxLimNom": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.WMinInLimNom": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.WMinLimNom": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Metering.GridMs.A.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.Metering.GridMs.A.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.Metering.GridMs.A.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.Metering.GridMs.PhV.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.Metering.GridMs.PhV.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.Metering.GridMs.PhV.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.Metering.GridMs.TotPF": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,  # TODO Measurement.Metering.GridMs.TotPF unit is not validated
    ),
    "Measurement.Metering.GridMs.TotVA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.TotVAr": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.TotWIn": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Metering.GridMs.TotWOut": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Metering.GridMs.TotWhIn": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.GridMs.TotWhOut": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.GridMs.VA.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VA.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VA.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VAr.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VAr.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VAr.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.W.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.WATT
    ),
    "Measurement.Metering.GridMs.W.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.WATT
    ),
    "Measurement.Metering.GridMs.W.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.WATT
    ),
    "Measurement.Bat.Amp": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY, unit=SMAUnit.AMPERE
    ),
    "Measurement.Bat.ChaStt": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Bat.Diag.ActlCapacNom": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PERCENT,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Bat.Diag.CapacThrpCnt": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PLAIN_NUMBER,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Bat.Diag.ChaAMax": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.AMPERE,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Bat.Diag.CntErrOvV": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PLAIN_NUMBER,
        category=SMAChannelCategory.DIAGNOSTIC,
        cumulative_mode=SMACumulativeMode.COUNTER,
    ),
    "Measurement.Bat.Diag.CntWrnOvV": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PLAIN_NUMBER,
        category=SMAChannelCategory.DIAGNOSTIC,
        cumulative_mode=SMACumulativeMode.COUNTER,
    ),
    "Measurement.Bat.Diag.CntWrnSOCLo": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PLAIN_NUMBER,
        category=SMAChannelCategory.DIAGNOSTIC,
        cumulative_mode=SMACumulativeMode.COUNTER,
    ),
    "Measurement.Bat.Diag.DschAMax": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.AMPERE,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Bat.Diag.StatTm": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.SECONDS,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Bat.Diag.TmpValMax": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.CELSIUS,
        category=SMAChannelCategory.DIAGNOSTIC,
        cumulative_mode=SMACumulativeMode.MAXIMUM,
    ),
    "Measurement.Bat.Diag.TmpValMin": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.CELSIUS,
        category=SMAChannelCategory.DIAGNOSTIC,
        cumulative_mode=SMACumulativeMode.MINIMUM,
    ),
    "Measurement.Bat.Diag.TotAhIn": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.AMPERE,
        category=SMAChannelCategory.DIAGNOSTIC,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Bat.Diag.TotAhOut": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.AMPERE,
        category=SMAChannelCategory.DIAGNOSTIC,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Bat.Diag.VolMax": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.VOLT,
        category=SMAChannelCategory.DIAGNOSTIC,
        cumulative_mode=SMACumulativeMode.MAXIMUM,
    ),
    "Measurement.Bat.TmpVal": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.CELSIUS,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Bat.Vol": KnownChannelEntry(
        device_kind=SMADeviceKind.BATTERY, unit=SMAUnit.VOLT
    ),
    "Measurement.Coolsys.Inverter.TmpVal": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.CELSIUS,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Coolsys.Inverter.TmpVal[]": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.CELSIUS,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.Coolsys.Tr.TmpVal": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.CELSIUS,
        category=SMAChannelCategory.DIAGNOSTIC,
    ),
    "Measurement.ExtGridMs.A.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.ExtGridMs.A.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.ExtGridMs.A.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.ExtGridMs.Hz": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.HERTZ,
    ),
    "Measurement.ExtGridMs.HzMax": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.HERTZ,
        cumulative_mode=SMACumulativeMode.MAXIMUM,
    ),
    "Measurement.ExtGridMs.HzMin": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.HERTZ,
        cumulative_mode=SMACumulativeMode.MINIMUM,
    ),
    "Measurement.ExtGridMs.PhV.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.ExtGridMs.PhV.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.ExtGridMs.PhV.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.ExtGridMs.TotA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.ExtGridMs.TotVAr": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.ExtGridMs.TotW": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.ExtGridMs.TotWhIn": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.ExtGridMs.TotWhOut": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.ExtGridMs.VAr.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.ExtGridMs.VAr.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.ExtGridMs.VAr.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.ExtGridMs.W.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.ExtGridMs.W.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.ExtGridMs.W.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.GridMs.A.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.GridMs.A.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.GridMs.A.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.GridMs.Hz": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.HERTZ
    ),
    "Measurement.GridMs.PhV.phsA": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.GridMs.PhV.phsB": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.GridMs.PhV.phsC": KnownChannelEntry(
        device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.DcMs.Vol[]": KnownChannelEntry(
        device_kind=SMADeviceKind.PV, unit=SMAUnit.VOLT
    ),
    "Measurement.DcMs.Amp[]": KnownChannelEntry(
        device_kind=SMADeviceKind.PV, unit=SMAUnit.AMPERE
    ),
    "Measurement.DcMs.Watt[]": KnownChannelEntry(
        device_kind=SMADeviceKind.PV, unit=SMAUnit.WATT
    ),
    "Measurement.MltFncSw.SttMstr": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.ENUM,
        enum_values=__COMMON_ENUM_VALUES,  # TODO: Measurement.MltFncSw.SttMstr enum_values may be partially incorrect, only [303] are validated
    ),
    "Measurement.Portal.EnnexOS.ConnStt": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.ENUM,
        category=SMAChannelCategory.DIAGNOSTIC,
        enum_values=__CONNECTION_STATUS_ENUM_VALUES,  # TODO: Measurement.Portal.EnnexOS.ConnStt enum_values may be partially incorrect, only [307] are validated
    ),
    "Measurement.WebConn.Stt": KnownChannelEntry(
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.ENUM,
        category=SMAChannelCategory.DIAGNOSTIC,
        enum_values=__CONNECTION_STATUS_ENUM_VALUES,  # TODO: Measurement.WebConn.Stt enum_values may be partially incorrect, only [307] are validated
    ),
}


def get_known_channel(channel_id: str) -> KnownChannelEntry | None:
    """Get known channel by channel_id.

    this function handles array channels with arbitrary index automatically.
    """

    # replace array index brackets with empty brackets
    if channel_id.endswith("]"):
        bracket_start = channel_id.rfind("[")
        channel_id = f"{channel_id[0:bracket_start]}[]"

    # get known channel
    return __KNOWN_CHANNELS.get(channel_id, None)
