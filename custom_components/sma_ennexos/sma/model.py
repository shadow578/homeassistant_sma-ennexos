"""SMA Api model classes."""

from datetime import datetime, timedelta


class SMAApiClientError(Exception):
    """Exception to indicate a general API error."""


class SMAApiCommunicationError(SMAApiClientError):
    """Exception to indicate a communication error."""


class SMAApiAuthenticationError(SMAApiClientError):
    """Exception to indicate an authentication error."""


class SMAApiParsingError(SMAApiClientError):
    """Exception to indicate a parsing error."""


class AuthTokenInfo:
    """sma auth token info."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

    granted_at: datetime

    def __init__(
        self, access_token: str, refresh_token: str, token_type: str, expires_in: int
    ) -> None:
        """Initialize auth token info."""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in

        self.granted_at = datetime.now()

    @property
    def time_until_expiration(self) -> timedelta:
        """Get the time until the token expires."""
        expires_at = self.granted_at + timedelta(seconds=self.expires_in)
        return expires_at - datetime.now()

    @property
    def seconds_until_expiration(self) -> int:
        """Get the seconds until the token expires."""
        return int(self.time_until_expiration.total_seconds())

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return self.seconds_until_expiration <= 0

    @classmethod
    def from_dict(cls, data: dict) -> "AuthTokenInfo":
        """Create from dict, verify required fields and their types."""
        if not isinstance(data, dict):
            raise SMAApiParsingError("auth token info is not a dict")

        if "access_token" not in data:
            raise SMAApiParsingError("missing field 'access_token' in auth token info")
        if "refresh_token" not in data:
            raise SMAApiParsingError("missing field 'refresh_token' in auth token info")
        if "token_type" not in data:
            raise SMAApiParsingError("missing field 'token_type' in auth token info")
        if "expires_in" not in data:
            raise SMAApiParsingError("missing field 'expires_in' in auth token info")

        if not isinstance(data["access_token"], str):
            raise SMAApiParsingError(
                "field 'access_token' in auth token info is not a string"
            )
        if not isinstance(data["refresh_token"], str):
            raise SMAApiParsingError(
                "field 'refresh_token' in auth token info is not a string"
            )
        if not isinstance(data["token_type"], str):
            raise SMAApiParsingError(
                "field 'token_type' in auth token info is not a string"
            )
        if not isinstance(data["expires_in"], int):
            raise SMAApiParsingError(
                "field 'expires_in' in auth token info is not an int"
            )

        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data["token_type"],
            expires_in=data["expires_in"],
        )


class TimeValuePair:
    """a single value at a single point in time."""

    time: str
    value: str | int | float | None

    def __init__(self, time: str, value: str | int | float | None) -> None:
        """Initialize time value pair."""
        self.time = time
        self.value = value

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
            if not isinstance(data["value"], str | int | float):
                raise SMAApiParsingError(
                    "field 'value' in time value pair is not a string, int or float"
                )
        else:
            data["value"] = None

        return cls(time=data["time"], value=data["value"])


class ChannelValues:
    """a value of a single channel of a single component."""

    channel_id: str
    component_id: str
    values: list[TimeValuePair]

    def __init__(
        self, channel_id: str, component_id: str, values: list[TimeValuePair]
    ) -> None:
        """Initialize channel values."""
        self.channel_id = channel_id
        self.component_id = component_id
        self.values = values

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


class ComponentInfo:
    """information about a component (e.g. a device)."""

    component_id: str
    component_type: str
    name: str

    serial_number: str | None
    firmware_version: str | None

    def __init__(
        self,
        component_id: str,
        component_type: str,
        name: str,
        serial_number: str | None = None,
        firmware_version: str | None = None,
    ) -> None:
        """Initialize component info."""
        self.component_id = component_id
        self.component_type = component_type
        self.name = name
        self.serial_number = serial_number
        self.firmware_version = firmware_version

    def add_extra(self, extra_data: dict) -> None:
        """Add optional extra data to this component info."""
        # extra data (all are optional)
        if isinstance(extra_data, dict):
            # serial number
            # (extra_data.serial)
            if "serial" in extra_data and isinstance(extra_data["serial"], str):
                self.serial_number = extra_data["serial"]

            # firmware version
            # (extra_data.deviceInfoFeatures[? where infoWidgetType = "FirmwareVersion"].value)
            if "deviceInfoFeatures" in extra_data and isinstance(
                extra_data["deviceInfoFeatures"], list
            ):
                for feature in extra_data["deviceInfoFeatures"]:
                    if (
                        isinstance(feature, dict)
                        and "infoWidgetType" in feature
                        and feature["infoWidgetType"] == "FirmwareVersion"
                        and "value" in feature
                        and isinstance(feature["value"], str)
                    ):
                        self.firmware_version = feature["value"]
                        break

    @classmethod
    def from_dict(cls, data: dict) -> "ComponentInfo":
        """Create from dict, verify required fields and their types."""
        if not isinstance(data, dict):
            raise SMAApiParsingError("component info is not a dict")

        if "componentId" not in data:
            raise SMAApiParsingError("missing field 'componentId' in component info")
        if "componentType" not in data:
            raise SMAApiParsingError("missing field 'componentType' in component info")
        if "name" not in data:
            raise SMAApiParsingError("missing field 'name' in component info")

        if not isinstance(data["componentId"], str):
            raise SMAApiParsingError(
                "field 'componentId' in component info is not a string"
            )
        if not isinstance(data["componentType"], str):
            raise SMAApiParsingError(
                "field 'componentType' in component info is not a string"
            )
        if not isinstance(data["name"], str):
            raise SMAApiParsingError("field 'name' in component info is not a string")

        return cls(
            component_id=data["componentId"],
            component_type=data["componentType"],
            name=data["name"],
        )


class LiveMeasurementQueryItem:
    """item for live measurement query."""

    component_id: str
    channel_id: str

    def __init__(self, component_id: str, channel_id: str) -> None:
        """Initialize live measurement query item."""
        self.component_id = component_id
        self.channel_id = channel_id

    def to_dict(self) -> dict:
        """Convert to dict."""
        return {"componentId": self.component_id, "channelId": self.channel_id}
