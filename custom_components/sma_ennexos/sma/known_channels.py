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
    SECOND = "second"
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


__COMMON_ENUM_VALUES = {
    55: "Communication error",
    303: "Off",
    304: "Island operation",
    305: "Island operation",
    306: "SMA island operation 60 Hz",
    307: "Ok",
    308: "On",
    309: "Operating",
    310: "General operating mode",
    311: "Open",
    312: "Phase assignment",
    313: "SMA island operation 50 Hz",
    314: "Maximum active power",
    315: "Maximum active power output",
    316: "Active power setpoint operating mode",
    317: "All phases",
    318: "Overload",
    319: "Overtemperature",
    454: "Calibration",
    455: "Warning",
    456: "Waiting for DC start conditions",
    457: "Waiting for grid voltage",
}


@dataclass
class KnownChannelEntry:
    """Entry in the __KNOWN_CHANNELS dict."""

    # human readable name for this channel
    name: str

    # kind of device this channel belongs to
    device_kind: str

    # unit of the channel value
    unit: str

    # optional cumulative mode
    cumulative_mode: str | None = None

    # optional list of enum values, only with unit=SMAUnit.ENUM
    enum_values: dict[int, str] | None = None

    # optional value when the channel is not available
    value_when_none: SMAValue | None = None


__KNOWN_CHANNELS: dict[
    str,
    KnownChannelEntry,
] = {
    "Measurement.GridMs.TotVAr": KnownChannelEntry(
        name="Grid Reactive Power",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.GridMs.TotVAr.Pv": KnownChannelEntry(
        name="PV Reactive Power",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.GridMs.TotW": KnownChannelEntry(
        name="Grid Power",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.GridMs.TotW.Pv": KnownChannelEntry(
        name="PV Power",
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Inverter.CurWCtlNom": KnownChannelEntry(
        name="Active Power Limit", device_kind=SMADeviceKind.PV, unit=SMAUnit.PERCENT
    ),
    "Measurement.Inverter.WAval": KnownChannelEntry(
        name="Available Inverter Power", device_kind=SMADeviceKind.PV, unit=SMAUnit.WATT
    ),
    "Measurement.Metering.GridMs.TotWIn.Bat": KnownChannelEntry(
        name="Power drawn by Battery",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Metering.GridMs.TotWOut.Bat": KnownChannelEntry(
        name="Power fed into Battery",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Metering.GridMs.TotWhIn.Bat": KnownChannelEntry(
        name="total power drawn by Battery",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.GridMs.TotWhOut.Bat": KnownChannelEntry(
        name="total power fed into Battery",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.PCCMs.PlntA.phsA": KnownChannelEntry(
        name="Grid interconnection current L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.Metering.PCCMs.PlntA.phsB": KnownChannelEntry(
        name="Grid interconnection current L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.Metering.PCCMs.PlntA.phsC": KnownChannelEntry(
        name="Grid interconnection current L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.Metering.PCCMs.PlntCsmpW": KnownChannelEntry(
        name="Power drawn from grid", device_kind=SMADeviceKind.GRID, unit=SMAUnit.WATT
    ),
    "Measurement.Metering.PCCMs.PlntCsmpWh": KnownChannelEntry(
        name="Total power drawn from grid",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.PCCMs.PlntPF": KnownChannelEntry(
        name="Grid interconnection displacement power factor",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,  # TODO Measurement.Metering.PCCMs.PlntPF unit is not validated
    ),
    "Measurement.Metering.PCCMs.PlntPhV.phsA": KnownChannelEntry(
        name="Grid interconnection voltage L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.Metering.PCCMs.PlntPhV.phsB": KnownChannelEntry(
        name="Grid interconnection voltage L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.Metering.PCCMs.PlntPhV.phsC": KnownChannelEntry(
        name="Grid interconnection voltage L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.Metering.PCCMs.PlntVAr": KnownChannelEntry(
        name="Grid interconnection reactive power",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.PCCMs.PlntVAr.phsA": KnownChannelEntry(
        name="Grid interconnection reactive power L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.PCCMs.PlntVAr.phsB": KnownChannelEntry(
        name="Grid interconnection reactive power L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.PCCMs.PlntVAr.phsC": KnownChannelEntry(
        name="Grid interconnection reactive power L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.PCCMs.PlntW": KnownChannelEntry(
        name="Grid interconnection power feed-in",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.Metering.PCCMs.PlntW.phsA": KnownChannelEntry(
        name="Grid interconnection power feed-in L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.Metering.PCCMs.PlntW.phsB": KnownChannelEntry(
        name="Grid interconnection power feed-in L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.Metering.PCCMs.PlntW.phsC": KnownChannelEntry(
        name="Grid interconnection power feed-in L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.Metering.PCCMs.PlntWh": KnownChannelEntry(
        name="Grid interconnection total power feed-in",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.TotWhOut.Pv": KnownChannelEntry(
        name="Total PV yield",
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Operation.CurAvailPlnt": KnownChannelEntry(
        name="Generation plant availability",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.CurAvailVArOvExt": KnownChannelEntry(
        name="available overexcited reactive power",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Operation.CurAvailVArOvExtNom": KnownChannelEntry(
        name="available overexcited reactive power",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.CurAvailVArUnExt": KnownChannelEntry(
        name="available underexcited reactive power",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Operation.CurAvailVArUnExtNom": KnownChannelEntry(
        name="available underexcited reactive power",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.Health": KnownChannelEntry(
        name="device health status",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.ENUM,
        enum_values=__COMMON_ENUM_VALUES,  # TODO: Measurement.Operation.Health enum_values may be partially incorrect, only [55, 307, 455] are validated
    ),
    "Measurement.Operation.WMaxInLimNom": KnownChannelEntry(
        name="maximum active power setpoint (grid supply)",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.WMaxLimNom": KnownChannelEntry(
        name="maximum active power setpoint specification",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.WMinInLimNom": KnownChannelEntry(
        name="minimum active power setpoint (grid supply)",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Operation.WMinLimNom": KnownChannelEntry(
        name="minimum active power setpoint specification",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Metering.GridMs.A.phsA": KnownChannelEntry(
        name="Grid current L1", device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.Metering.GridMs.A.phsB": KnownChannelEntry(
        name="Grid current L2", device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.Metering.GridMs.A.phsC": KnownChannelEntry(
        name="Grid current L3", device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.Metering.GridMs.PhV.phsA": KnownChannelEntry(
        name="Grid voltage L1", device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.Metering.GridMs.PhV.phsB": KnownChannelEntry(
        name="Grid voltage L2", device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.Metering.GridMs.PhV.phsC": KnownChannelEntry(
        name="Grid voltage L3", device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.Metering.GridMs.TotPF": KnownChannelEntry(
        name="Grid displacement power factor",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.PERCENT,  # TODO Measurement.Metering.GridMs.TotPF unit is not validated
    ),
    "Measurement.Metering.GridMs.TotVA": KnownChannelEntry(
        name="Grid apparent power",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.TotVAr": KnownChannelEntry(
        name="Grid reactive power",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.TotWIn": KnownChannelEntry(
        name="Grid power drawn",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Metering.GridMs.TotWOut": KnownChannelEntry(
        name="Grid power fed-in",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.Metering.GridMs.TotWhIn": KnownChannelEntry(
        name="Total power drawn from grid",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.GridMs.TotWhOut": KnownChannelEntry(
        name="Total power fed into grid",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Metering.GridMs.VA.phsA": KnownChannelEntry(
        name="Grid apparent power L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VA.phsB": KnownChannelEntry(
        name="Grid apparent power L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VA.phsC": KnownChannelEntry(
        name="Grid apparent power L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VAr.phsA": KnownChannelEntry(
        name="Grid reactive power L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VAr.phsB": KnownChannelEntry(
        name="Grid reactive power L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.VAr.phsC": KnownChannelEntry(
        name="Grid reactive power L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.Metering.GridMs.W.phsA": KnownChannelEntry(
        name="Grid power drawn L1", device_kind=SMADeviceKind.GRID, unit=SMAUnit.WATT
    ),
    "Measurement.Metering.GridMs.W.phsB": KnownChannelEntry(
        name="Grid power drawn L2", device_kind=SMADeviceKind.GRID, unit=SMAUnit.WATT
    ),
    "Measurement.Metering.GridMs.W.phsC": KnownChannelEntry(
        name="Grid power drawn L3", device_kind=SMADeviceKind.GRID, unit=SMAUnit.WATT
    ),
    "Measurement.Bat.Amp": KnownChannelEntry(
        name="Battery current", device_kind=SMADeviceKind.BATTERY, unit=SMAUnit.AMPERE
    ),
    "Measurement.Bat.ChaStt": KnownChannelEntry(
        name="Battery Charge State",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Bat.Diag.ActlCapacNom": KnownChannelEntry(
        name="current battery capacity",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PERCENT,
    ),
    "Measurement.Bat.Diag.CapacThrpCnt": KnownChannelEntry(
        name="battery charge cycles",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PLAIN_NUMBER,
    ),
    "Measurement.Bat.Diag.ChaAMax": KnownChannelEntry(
        name="maximum charge current",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.Bat.Diag.CntErrOvV": KnownChannelEntry(
        name="battery overvoltage error count",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PLAIN_NUMBER,
        cumulative_mode=SMACumulativeMode.COUNTER,
    ),
    "Measurement.Bat.Diag.CntWrnOvV": KnownChannelEntry(
        name="battery overvoltage warning count",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PLAIN_NUMBER,
        cumulative_mode=SMACumulativeMode.COUNTER,
    ),
    "Measurement.Bat.Diag.CntWrnSOCLo": KnownChannelEntry(
        name="battery low SOC warning count",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.PLAIN_NUMBER,
        cumulative_mode=SMACumulativeMode.COUNTER,
    ),
    "Measurement.Bat.Diag.DschAMax": KnownChannelEntry(
        name="maximum discharge current",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.Bat.Diag.StatTm": KnownChannelEntry(
        name="battery operating time",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.SECOND,
    ),
    "Measurement.Bat.Diag.TmpValMax": KnownChannelEntry(
        name="maximum battery temperature",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.CELSIUS,
        cumulative_mode=SMACumulativeMode.MAXIMUM,
    ),
    "Measurement.Bat.Diag.TmpValMin": KnownChannelEntry(
        name="minimum battery temperature",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.CELSIUS,
        cumulative_mode=SMACumulativeMode.MINIMUM,
    ),
    "Measurement.Bat.Diag.TotAhIn": KnownChannelEntry(
        name="total battery charge",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.AMPERE,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Bat.Diag.TotAhOut": KnownChannelEntry(
        name="total battery discharge",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.AMPERE,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.Bat.Diag.VolMax": KnownChannelEntry(
        name="maximum battery voltage",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.VOLT,
        cumulative_mode=SMACumulativeMode.MAXIMUM,
    ),
    "Measurement.Bat.TmpVal": KnownChannelEntry(
        name="Battery temperature",
        device_kind=SMADeviceKind.BATTERY,
        unit=SMAUnit.CELSIUS,
    ),
    "Measurement.Bat.Vol": KnownChannelEntry(
        name="Battery voltage", device_kind=SMADeviceKind.BATTERY, unit=SMAUnit.VOLT
    ),
    "Measurement.Coolsys.Inverter.TmpVal": KnownChannelEntry(
        name="Inverter temperature",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.CELSIUS,
    ),
    "Measurement.Coolsys.Tr.TmpVal": KnownChannelEntry(
        name="Transformer temperature",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.CELSIUS,
    ),
    "Measurement.ExtGridMs.A.phsA": KnownChannelEntry(
        name="external grid current L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.ExtGridMs.A.phsB": KnownChannelEntry(
        name="external grid current L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.ExtGridMs.A.phsC": KnownChannelEntry(
        name="external grid current L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.ExtGridMs.Hz": KnownChannelEntry(
        name="external grid frequency",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.HERTZ,
    ),
    "Measurement.ExtGridMs.HzMax": KnownChannelEntry(
        name="maximum external grid frequency",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.HERTZ,
        cumulative_mode=SMACumulativeMode.MAXIMUM,
    ),
    "Measurement.ExtGridMs.HzMin": KnownChannelEntry(
        name="minimum external grid frequency",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.HERTZ,
        cumulative_mode=SMACumulativeMode.MINIMUM,
    ),
    "Measurement.ExtGridMs.PhV.phsA": KnownChannelEntry(
        name="external grid voltage L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.ExtGridMs.PhV.phsB": KnownChannelEntry(
        name="external grid voltage L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.ExtGridMs.PhV.phsC": KnownChannelEntry(
        name="external grid voltage L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT,
    ),
    "Measurement.ExtGridMs.TotA": KnownChannelEntry(
        name="external grid current",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.AMPERE,
    ),
    "Measurement.ExtGridMs.TotVAr": KnownChannelEntry(
        name="external grid reactive power",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.ExtGridMs.TotW": KnownChannelEntry(
        name="external grid power output",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
        value_when_none=0,
    ),
    "Measurement.ExtGridMs.TotWhIn": KnownChannelEntry(
        name="total power drawn from external grid",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.ExtGridMs.TotWhOut": KnownChannelEntry(
        name="total power fed into external grid",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    ),
    "Measurement.ExtGridMs.VAr.phsA": KnownChannelEntry(
        name="external grid reactive power L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.ExtGridMs.VAr.phsB": KnownChannelEntry(
        name="external grid reactive power L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.ExtGridMs.VAr.phsC": KnownChannelEntry(
        name="external grid reactive power L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.VOLT_AMPERE_REACTIVE,
    ),
    "Measurement.ExtGridMs.W.phsA": KnownChannelEntry(
        name="external grid power output L1",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.ExtGridMs.W.phsB": KnownChannelEntry(
        name="external grid power output L2",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.ExtGridMs.W.phsC": KnownChannelEntry(
        name="external grid power output L3",
        device_kind=SMADeviceKind.GRID,
        unit=SMAUnit.WATT,
    ),
    "Measurement.GridMs.A.phsA": KnownChannelEntry(
        name="grid current L1", device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.GridMs.A.phsB": KnownChannelEntry(
        name="grid current L2", device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.GridMs.A.phsC": KnownChannelEntry(
        name="grid current L3", device_kind=SMADeviceKind.GRID, unit=SMAUnit.AMPERE
    ),
    "Measurement.GridMs.Hz": KnownChannelEntry(
        name="grid frequency", device_kind=SMADeviceKind.GRID, unit=SMAUnit.HERTZ
    ),
    "Measurement.GridMs.PhV.phsA": KnownChannelEntry(
        name="grid voltage L1", device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.GridMs.PhV.phsB": KnownChannelEntry(
        name="grid voltage L2", device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.GridMs.PhV.phsC": KnownChannelEntry(
        name="grid voltage L3", device_kind=SMADeviceKind.GRID, unit=SMAUnit.VOLT
    ),
    "Measurement.DcMs.Vol[]": KnownChannelEntry(
        name="dc voltage", device_kind=SMADeviceKind.PV, unit=SMAUnit.VOLT
    ),
    "Measurement.DcMs.Amp[]": KnownChannelEntry(
        name="dc current", device_kind=SMADeviceKind.PV, unit=SMAUnit.AMPERE
    ),
    "Measurement.DcMs.Watt[]": KnownChannelEntry(
        name="dc power", device_kind=SMADeviceKind.PV, unit=SMAUnit.WATT
    ),
    "Measurement.MltFncSw.SttMstr": KnownChannelEntry(
        name="multi-function relay status",
        device_kind=SMADeviceKind.OTHER,
        unit=SMAUnit.ENUM,
        enum_values=__COMMON_ENUM_VALUES,  # TODO: Measurement.MltFncSw.SttMstr enum_values may be partially incorrect, only [303] are validated
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
