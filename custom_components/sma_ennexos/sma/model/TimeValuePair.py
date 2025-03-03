"""SMA Time/Value Pair."""

from dataclasses import dataclass

from .errors import SMAApiParsingError

SMAValue = str | int | float


@dataclass
class TimeValuePair:
    """a single value at a single point in time."""

    time: str
    value: SMAValue | None

    @classmethod
    def from_dict(cls, data: dict) -> "TimeValuePair":
        """Create from dict, verify required fields and their types."""
        if not isinstance(data, dict):
            raise SMAApiParsingError("time value pair is not a dict")

        if "time" not in data:
            raise SMAApiParsingError("missing field 'time' in time value pair")

        if not isinstance(data["time"], str):
            raise SMAApiParsingError("field 'time' in time value pair is not a string")

        # value is optional
        if "value" in data:
            if not isinstance(data["value"], SMAValue):
                raise SMAApiParsingError(
                    "field 'value' in time value pair is not a SMAValue"
                )
        else:
            data["value"] = None

        return cls(time=data["time"], value=data["value"])
