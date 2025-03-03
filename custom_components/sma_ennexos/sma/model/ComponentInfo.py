"""SMA component / device information."""

from .errors import SMAApiParsingError


class ComponentInfo:
    """information about a component (e.g. a device)."""

    component_id: str
    component_type: str
    name: str

    model_name: str | None
    serial_number: str | None
    firmware_version: str | None

    def __init__(
        self,
        component_id: str,
        component_type: str,
        name: str,
        model_name: str | None = None,
        serial_number: str | None = None,
        firmware_version: str | None = None,
    ) -> None:
        """Initialize component info."""
        self.component_id = component_id
        self.component_type = component_type
        self.name = name
        self.model_name = model_name
        self.serial_number = serial_number
        self.firmware_version = firmware_version

    def add_extra(self, extra_data: dict) -> None:
        """Add optional extra data to this component info."""
        # extra data (all are optional)
        if isinstance(extra_data, dict):
            # model name
            if "name" in extra_data and isinstance(extra_data["name"], str):
                self.model_name = extra_data["name"]

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
