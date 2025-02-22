"""SMA known channels."""

from typing import TypedDict

UNIT_PLAIN_NUMBER: str = "PLAIN_NUMBER"
UNIT_VOLT: str = "VOLT"
UNIT_AMPERE: str = "AMPERE"
UNIT_WATT: str = "WATT"
UNIT_WATT_HOUR: str = "WATT_HOUR"
UNIT_CELSIUS: str = "CELSIUS"
UNIT_HERTZ: str = "HERTZ"
UNIT_VOLT_AMPERE_REACTIVE: str = "VOLT_AMPERE_REACTIVE"
UNIT_SECOND: str = "SECOND"
UNIT_PERCENT: str = "PERCENT"
UNIT_ENUM: str = "ENUM"  # SMA enum, value keys defined in KnownChannel enum_values dict

DEVICE_KIND_GRID: str = "GRID"
DEVICE_KIND_BATTERY: str = "BATTERY"
DEVICE_KIND_PV: str = "PV"
DEVICE_KIND_OTHER: str = "OTHER"

CUMULATIVE_MODE_NONE: str = "NONE"  # no cummulative, one-time measurement
CUMULATIVE_MODE_COUNTER: str = (
    "COUNTER"  # increasing counter value, e.g. error count, operating time
)
CUMULATIVE_MODE_TOTAL: str = "TOTAL"  # total value, e.g. yield
CUMULATIVE_MODE_MINIMUM: str = (
    "MINIMUM"  # minimum measurement, e.g. minimum temperature
)
CUMULATIVE_MODE_MAXIMUM: str = (
    "MAXIMUM"  # maximum measurement, e.g. maximum temperature
)

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


class KnownChannelEntry(TypedDict):
    """Entry in the __KNOWN_CHANNELS dict."""

    name: str
    device_kind: str
    unit: str
    cumulative_mode: str | None
    enum_values: dict[int, str] | None


__KNOWN_CHANNELS: dict[
    str,
    KnownChannelEntry,
] = {
    "Measurement.GridMs.TotVAr": {
        "name": "Grid Reactive Power",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.GridMs.TotVAr.Pv": {
        "name": "PV Reactive Power",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.GridMs.TotW": {
        "name": "Grid Power",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.GridMs.TotW.Pv": {
        "name": "PV Power",
        "device_kind": DEVICE_KIND_PV,
        "unit": UNIT_WATT,
    },
    "Measurement.Inverter.CurWCtlNom": {
        "name": "Active Power Limit",
        "device_kind": DEVICE_KIND_PV,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Inverter.WAval": {
        "name": "Available Inverter Power",
        "device_kind": DEVICE_KIND_PV,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.GridMs.TotWIn.Bat": {
        "name": "Power drawn by Battery",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.GridMs.TotWOut.Bat": {
        "name": "Power fed into Battery",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.GridMs.TotWhIn.Bat": {
        "name": "total power drawn by Battery",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Metering.GridMs.TotWhOut.Bat": {
        "name": "total power fed into Battery",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Metering.PCCMs.PlntA.phsA": {
        "name": "Grid interconnection current L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Metering.PCCMs.PlntA.phsB": {
        "name": "Grid interconnection current L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Metering.PCCMs.PlntA.phsC": {
        "name": "Grid interconnection current L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Metering.PCCMs.PlntCsmpW": {
        "name": "Power drawn from grid",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.PCCMs.PlntCsmpWh": {
        "name": "Total power drawn from grid",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Metering.PCCMs.PlntPF": {
        "name": "Grid interconnection displacement power factor",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_PERCENT,  # ?
    },
    "Measurement.Metering.PCCMs.PlntPhV.phsA": {
        "name": "Grid interconnection voltage L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.Metering.PCCMs.PlntPhV.phsB": {
        "name": "Grid interconnection voltage L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.Metering.PCCMs.PlntPhV.phsC": {
        "name": "Grid interconnection voltage L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.Metering.PCCMs.PlntVAr": {
        "name": "Grid interconnection reactive power",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.PCCMs.PlntVAr.phsA": {
        "name": "Grid interconnection reactive power L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.PCCMs.PlntVAr.phsB": {
        "name": "Grid interconnection reactive power L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.PCCMs.PlntVAr.phsC": {
        "name": "Grid interconnection reactive power L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.PCCMs.PlntW": {
        "name": "Grid interconnection power feed-in",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.PCCMs.PlntW.phsA": {
        "name": "Grid interconnection power feed-in L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.PCCMs.PlntW.phsB": {
        "name": "Grid interconnection power feed-in L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.PCCMs.PlntW.phsC": {
        "name": "Grid interconnection power feed-in L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.PCCMs.PlntWh": {
        "name": "Grid interconnection total power feed-in",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Metering.TotWhOut.Pv": {
        "name": "Total PV yield",
        "device_kind": DEVICE_KIND_PV,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Operation.CurAvailPlnt": {
        "name": "Generation plant availability",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Operation.CurAvailVArOvExt": {
        "name": "available overexcited reactive power",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Operation.CurAvailVArOvExtNom": {
        "name": "available overexcited reactive power",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Operation.CurAvailVArUnExt": {
        "name": "available underexcited reactive power",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Operation.CurAvailVArUnExtNom": {
        "name": "available underexcited reactive power",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Operation.Health": {
        "name": "device health status",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_ENUM,
        "enum_values": __COMMON_ENUM_VALUES,  # TODO: Measurement.Operation.Health enum_values may be partially incorrect, only [55, 307, 455] are validated
    },
    "Measurement.Operation.WMaxInLimNom": {
        "name": "maximum active power setpoint (grid supply)",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Operation.WMaxLimNom": {
        "name": "maximum active power setpoint specification",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Operation.WMinInLimNom": {
        "name": "minimum active power setpoint (grid supply)",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Operation.WMinLimNom": {
        "name": "minimum active power setpoint specification",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Metering.GridMs.A.phsA": {
        "name": "Grid current L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Metering.GridMs.A.phsB": {
        "name": "Grid current L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Metering.GridMs.A.phsC": {
        "name": "Grid current L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Metering.GridMs.PhV.phsA": {
        "name": "Grid voltage L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.Metering.GridMs.PhV.phsB": {
        "name": "Grid voltage L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.Metering.GridMs.PhV.phsC": {
        "name": "Grid voltage L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.Metering.GridMs.TotPF": {
        "name": "Grid displacement power factor",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_PERCENT,  # ?
    },
    "Measurement.Metering.GridMs.TotVA": {
        "name": "Grid apparent power",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.GridMs.TotVAr": {
        "name": "Grid reactive power",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.GridMs.TotWIn": {
        "name": "Grid power drawn",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.GridMs.TotWOut": {
        "name": "Grid power fed-in",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.GridMs.TotWhIn": {
        "name": "Total power drawn from grid",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Metering.GridMs.TotWhOut": {
        "name": "Total power fed into grid",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Metering.GridMs.VA.phsA": {
        "name": "Grid apparent power L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.GridMs.VA.phsB": {
        "name": "Grid apparent power L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.GridMs.VA.phsC": {
        "name": "Grid apparent power L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.GridMs.VAr.phsA": {
        "name": "Grid reactive power L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.GridMs.VAr.phsB": {
        "name": "Grid reactive power L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.GridMs.VAr.phsC": {
        "name": "Grid reactive power L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.Metering.GridMs.W.phsA": {
        "name": "Grid power drawn L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.GridMs.W.phsB": {
        "name": "Grid power drawn L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Metering.GridMs.W.phsC": {
        "name": "Grid power drawn L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.Bat.Amp": {
        "name": "Battery current",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Bat.ChaStt": {
        "name": "Battery Charge State",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Bat.Diag.ActlCapacNom": {
        "name": "current battery capacity",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_PERCENT,
    },
    "Measurement.Bat.Diag.CapacThrpCnt": {
        "name": "battery charge cycles",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_PLAIN_NUMBER,
    },
    "Measurement.Bat.Diag.ChaAMax": {
        "name": "maximum charge current",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Bat.Diag.CntErrOvV": {
        "name": "battery overvoltage error count",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_PLAIN_NUMBER,
        "cumulative_mode": CUMULATIVE_MODE_COUNTER,
    },
    "Measurement.Bat.Diag.CntWrnOvV": {
        "name": "battery overvoltage warning count",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_PLAIN_NUMBER,
        "cumulative_mode": CUMULATIVE_MODE_COUNTER,
    },
    "Measurement.Bat.Diag.CntWrnSOCLo": {
        "name": "battery low SOC warning count",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_PLAIN_NUMBER,
        "cumulative_mode": CUMULATIVE_MODE_COUNTER,
    },
    "Measurement.Bat.Diag.DschAMax": {
        "name": "maximum discharge current",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_AMPERE,
    },
    "Measurement.Bat.Diag.StatTm": {
        "name": "battery operating time",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_SECOND,
    },
    "Measurement.Bat.Diag.TmpValMax": {
        "name": "maximum battery temperature",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_CELSIUS,
        "cumulative_mode": CUMULATIVE_MODE_MAXIMUM,
    },
    "Measurement.Bat.Diag.TmpValMin": {
        "name": "minimum battery temperature",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_CELSIUS,
        "cumulative_mode": CUMULATIVE_MODE_MINIMUM,
    },
    "Measurement.Bat.Diag.TotAhIn": {
        "name": "total battery charge",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_AMPERE,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Bat.Diag.TotAhOut": {
        "name": "total battery discharge",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_AMPERE,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.Bat.Diag.VolMax": {
        "name": "maximum battery voltage",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_VOLT,
        "cumulative_mode": CUMULATIVE_MODE_MAXIMUM,
    },
    "Measurement.Bat.TmpVal": {
        "name": "Battery temperature",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_CELSIUS,
    },
    "Measurement.Bat.Vol": {
        "name": "Battery voltage",
        "device_kind": DEVICE_KIND_BATTERY,
        "unit": UNIT_VOLT,
    },
    "Measurement.Coolsys.Inverter.TmpVal": {
        "name": "Inverter temperature",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_CELSIUS,
    },
    "Measurement.Coolsys.Tr.TmpVal": {
        "name": "Transformer temperature",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_CELSIUS,
    },
    "Measurement.ExtGridMs.A.phsA": {
        "name": "external grid current L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.ExtGridMs.A.phsB": {
        "name": "external grid current L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.ExtGridMs.A.phsC": {
        "name": "external grid current L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.ExtGridMs.Hz": {
        "name": "external grid frequency",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_HERTZ,
    },
    "Measurement.ExtGridMs.HzMax": {
        "name": "maximum external grid frequency",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_HERTZ,
        "cumulative_mode": CUMULATIVE_MODE_MAXIMUM,
    },
    "Measurement.ExtGridMs.HzMin": {
        "name": "minimum external grid frequency",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_HERTZ,
        "cumulative_mode": CUMULATIVE_MODE_MINIMUM,
    },
    "Measurement.ExtGridMs.PhV.phsA": {
        "name": "external grid voltage L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.ExtGridMs.PhV.phsB": {
        "name": "external grid voltage L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.ExtGridMs.PhV.phsC": {
        "name": "external grid voltage L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.ExtGridMs.TotA": {
        "name": "external grid current",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.ExtGridMs.TotVAr": {
        "name": "external grid reactive power",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.ExtGridMs.TotW": {
        "name": "external grid power output",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.ExtGridMs.TotWhIn": {
        "name": "total power drawn from external grid",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.ExtGridMs.TotWhOut": {
        "name": "total power fed into external grid",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT_HOUR,
        "cumulative_mode": CUMULATIVE_MODE_TOTAL,
    },
    "Measurement.ExtGridMs.VAr.phsA": {
        "name": "external grid reactive power L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.ExtGridMs.VAr.phsB": {
        "name": "external grid reactive power L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.ExtGridMs.VAr.phsC": {
        "name": "external grid reactive power L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT_AMPERE_REACTIVE,
    },
    "Measurement.ExtGridMs.W.phsA": {
        "name": "external grid power output L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.ExtGridMs.W.phsB": {
        "name": "external grid power output L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.ExtGridMs.W.phsC": {
        "name": "external grid power output L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_WATT,
    },
    "Measurement.GridMs.A.phsA": {
        "name": "grid current L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.GridMs.A.phsB": {
        "name": "grid current L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.GridMs.A.phsC": {
        "name": "grid current L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_AMPERE,
    },
    "Measurement.GridMs.Hz": {
        "name": "grid frequency",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_HERTZ,
    },
    "Measurement.GridMs.PhV.phsA": {
        "name": "grid voltage L1",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.GridMs.PhV.phsB": {
        "name": "grid voltage L2",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.GridMs.PhV.phsC": {
        "name": "grid voltage L3",
        "device_kind": DEVICE_KIND_GRID,
        "unit": UNIT_VOLT,
    },
    "Measurement.DcMs.Vol[]": {
        "name": "dc voltage",
        "device_kind": DEVICE_KIND_PV,
        "unit": UNIT_VOLT,
    },
    "Measurement.DcMs.Amp[]": {
        "name": "dc current",
        "device_kind": DEVICE_KIND_PV,
        "unit": UNIT_AMPERE,
    },
    "Measurement.DcMs.Watt[]": {
        "name": "dc power",
        "device_kind": DEVICE_KIND_PV,
        "unit": UNIT_WATT,
    },
    "Measurement.MltFncSw.SttMstr": {
        "name": "multi-function relay status",
        "device_kind": DEVICE_KIND_OTHER,
        "unit": UNIT_ENUM,
        "enum_values": __COMMON_ENUM_VALUES,  # TODO: Measurement.MltFncSw.SttMstr enum_values may be partially incorrect, only [303] are validated
    },
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
