"""Measurement values of a single sensor channel."""

from dataclasses import dataclass

from .errors import SMAApiParsingError
from .TimeValuePair import TimeValuePair


@dataclass
class ChannelValues:
    """a value of a single channel of a single component."""

    channel_id: str
    component_id: str
    values: list[TimeValuePair]

    def latest_value(self) -> TimeValuePair:
        """Get the latest value."""
        if len(self.values) == 0:
            raise ValueError(
                f"no values available for {self.channel_id}@{self.component_id}"
            )
        return self.values[-1]

    @classmethod
    def __parse_dict(cls, data: dict) -> tuple[str, str, list[dict]]:
        """Parse channel info and values from dict.

        :returns: tuple of (channel_id, component_id, values)
        """
        if not isinstance(data, dict):
            raise SMAApiParsingError("channel values is not a dict")

        if "channelId" not in data:
            raise SMAApiParsingError("missing field 'channelId' in channel values")
        if "componentId" not in data:
            raise SMAApiParsingError("missing field 'componentId' in channel values")
        if "values" not in data:
            raise SMAApiParsingError("missing field 'values' in channel values")

        if not isinstance(data["channelId"], str):
            raise SMAApiParsingError(
                "field 'channelId' in channel values is not a string"
            )
        if not isinstance(data["componentId"], str):
            raise SMAApiParsingError(
                "field 'componentId' in channel values is not a string"
            )
        if not isinstance(data["values"], list):
            raise SMAApiParsingError("field 'values' in channel values is not a list")

        for v in data["values"]:
            if not isinstance(v, dict):
                raise SMAApiParsingError(
                    "element in 'values' in channel values is not a dict"
                )

        return (data["channelId"], data["componentId"], data["values"])

    @classmethod
    def from_dict(cls, data: dict) -> list["ChannelValues"]:
        """Create from dict, verify required fields and their types."""

        # parse channel info and values from dict
        channelId, componentId, values = cls.__parse_dict(data)

        # is this an array channel?
        if (
            len(values) >= 1  # has at least one value
            and "time" in values[0]  # has time field
            and isinstance(values[0]["time"], str)  # time field is a string
            and "values" in values[0]  # has values field
            and isinstance(values[0]["values"], list)  # values field is a list
        ):
            # TODO: in array channels, only the first value is used.
            # normally, this should be fine since no other values are ever returned by the api.
            # still, being able to handle multiple values would be more correct.

            # array channel:
            # trim "[]" from channel id
            channelId = channelId[:-2] if channelId.endswith("[]") else channelId

            # get shared time
            time = values[0]["time"]

            # manually create ChannelValues for each array value
            return [
                cls(
                    channel_id=f"{channelId}[{i}]",
                    component_id=componentId,
                    values=[TimeValuePair(time=time, value=value)],
                )
                for i, value in enumerate(values[0]["values"])
            ]
        else:
            # single-value channel:
            # convert all values to TimeValuePair
            values = [TimeValuePair.from_dict(v) for v in data["values"]]

            # create ChannelValue
            return [
                cls(
                    channel_id=channelId,
                    component_id=componentId,
                    values=values,
                )
            ]
