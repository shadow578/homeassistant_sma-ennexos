"""SMA component / device information."""

from dataclasses import dataclass

from .errors import SMAApiParsingError


@dataclass
class ComponentInfo:
    """information about a component (e.g. a device)."""

    component_id: str
    component_type: str
    name: str

    vendor: str | None = None
    product_name: str | None = None
    serial_number: str | None = None
    firmware_version: str | None = None
    ip_address: str | None = None
    generator_power: int | None = None

    product_tag_id: int | None = None

    def add_extra(self, extra_data: dict) -> None:
        """Add optional extra data to this component info."""
        # extra data (all are optional)
        if isinstance(extra_data, dict):
            # product name
            if self.product_name is None:
                # from /api/v1/plants/xxx/devices/xxx
                if "product" in extra_data and isinstance(extra_data["product"], str):
                    self.product_name = extra_data["product"]

                # from /api/v1/widgets/deviceinfo
                if "name" in extra_data and isinstance(extra_data["name"], str):
                    self.product_name = extra_data["name"]

            # product vendor
            if self.vendor is None:
                # from /api/v1/plants/xxx/devices/xxx
                if "vendor" in extra_data and isinstance(extra_data["vendor"], str):
                    self.vendor = extra_data["vendor"]

            # serial number
            if self.serial_number is None:
                # from /api/v1/plants/xxx/devices/xxx
                # and /api/v1/widgets/deviceinfo
                if "serial" in extra_data and isinstance(extra_data["serial"], str):
                    self.serial_number = extra_data["serial"]

            # firmware version
            if self.firmware_version is None:
                # from /api/v1/plants/xxx/devices/xxx
                if "firmwareVersion" in extra_data and isinstance(
                    extra_data["firmwareVersion"], str
                ):
                    self.firmware_version = extra_data["firmwareVersion"]

                # from /api/v1/widgets/deviceinfo
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

            # ip address
            if self.ip_address is None:
                # from /api/v1/plants/xxx/devices/xxx
                if "ipAddress" in extra_data and isinstance(
                    extra_data["ipAddress"], str
                ):
                    self.ip_address = extra_data["ipAddress"]

            # generator power
            if self.generator_power is None:
                # from /api/v1/plants/xxx/devices/xxx
                if "generatorPower" in extra_data and isinstance(
                    extra_data["generatorPower"], int
                ):
                    self.generator_power = extra_data["generatorPower"]

            # product tag id
            if self.product_tag_id is None:
                # from /api/v1/plants/xxx/devices/xxx
                # and /api/v1/widgets/deviceinfo
                if "productTagId" in extra_data and isinstance(
                    extra_data["productTagId"], int
                ):
                    self.product_tag_id = extra_data["productTagId"]

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
