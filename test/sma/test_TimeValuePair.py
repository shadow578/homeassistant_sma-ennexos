"""unit tests for model.TimeValuePair."""

import pytest

from custom_components.sma_ennexos.sma.model import SMAApiParsingError, TimeValuePair


def test_from_dict_valid_dict():
    """Test that TimeValuePair.from_dict() parses a valid dict correctly."""

    # call from_dict()
    time_value_pair = TimeValuePair.from_dict(
        {"time": "2024-02-01T11:25:46Z", "value": 300}
    )

    # check result
    assert time_value_pair.time == "2024-02-01T11:25:46Z"
    assert time_value_pair.value == 300


def test_from_dict_valid_no_value():
    """Test that TimeValuePair.from_dict() parses a valid dict correctly even if there is no value."""

    # call from_dict()
    time_value_pair = TimeValuePair.from_dict(
        {
            "time": "2024-02-01T11:25:46Z",
        }
    )

    # check result
    assert time_value_pair.time == "2024-02-01T11:25:46Z"
    assert time_value_pair.value is None


def test_from_dict_invalid_dict():
    """Test that TimeValuePair.from_dict() raises an exception if the dict is invalid."""

    with pytest.raises(SMAApiParsingError):
        TimeValuePair.from_dict({})
