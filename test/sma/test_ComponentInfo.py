"""unit tests for model.ComponentInfo."""

import pytest

from custom_components.sma_ennexos.sma.model import ComponentInfo, SMAApiParsingError


def test_from_dict_valid_dict():
    """Test that ComponentInfo.from_dict() parses a valid dict correctly."""

    # prepare dict
    component_info_dict = {
        "componentId": "The:Component-Id",
        "componentType": "TheComponentType",
        "name": "The Name",
    }

    # call from_dict()
    component_info = ComponentInfo.from_dict(component_info_dict)

    # check result
    assert component_info.component_id == "The:Component-Id"
    assert component_info.component_type == "TheComponentType"
    assert component_info.name == "The Name"

    # no extra
    assert component_info.serial_number is None
    assert component_info.firmware_version is None


def test_from_dict_invalid_dict():
    """Test that ComponentInfo.from_dict() raises an exception if the dict is invalid."""

    with pytest.raises(SMAApiParsingError):
        ComponentInfo.from_dict({})


def test_add_extra():
    """Test that ComponentInfo.add_extra() adds the extra info correctly."""

    # prepare component info object
    component_info = ComponentInfo.from_dict(
        {
            "componentId": "The:Component-Id",
            "componentType": "TheComponentType",
            "name": "The Name",
        }
    )

    # add extra info
    component_info.add_extra(
        {
            "serial": "TheSerial",
            "deviceInfoFeatures": [
                {"infoWidgetType": "FirmwareVersion", "value": "TheFirmwareVersion"}
            ],
        }
    )

    # check result
    assert component_info.component_id == "The:Component-Id"
    assert component_info.component_type == "TheComponentType"
    assert component_info.name == "The Name"
    assert component_info.serial_number == "TheSerial"
    assert component_info.firmware_version == "TheFirmwareVersion"
