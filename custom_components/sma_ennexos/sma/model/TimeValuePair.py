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
        value = None
        if "value" in data:
            if isinstance(data["value"], SMAValue):
                value = data["value"]
            else:
                raise SMAApiParsingError(
                    "field 'value' in time value pair is not a SMAValue"
                )
        # newer firmware started returning "NaN" as value instead of null
        # we treat "NaN" as None
        if isinstance(value, str) and value.lower() == "nan":
            value = None
        if isinstance(value, float) and value != value:
            value = None

        return cls(time=data["time"], value=value)
