"""unit tests for model.ChannelValues."""

import pytest

from custom_components.sma_ennexos.sma.model import ChannelValues, SMAApiParsingError


def test_from_dict_valid_dict():
    """Test that ChannelValues.from_dict() parses a valid dict correctly."""

    # prepare dict
    channel_values_dict = {
        "channelId": "TheChannelId",
        "componentId": "The:Component-Id",
        "values": [
            {"time": "2024-02-01T11:25:46Z", "value": 307},
            {"time": "2024-02-01T11:30:00Z", "value": 309},
        ],
    }

    # call from_dict()
    channel_values = ChannelValues.from_dict(channel_values_dict)

    # check result
    assert len(channel_values) == 1

    assert channel_values[0].channel_id == "TheChannelId"
    assert channel_values[0].component_id == "The:Component-Id"
    assert len(channel_values[0].values) == 2
    assert channel_values[0].values[0].time == "2024-02-01T11:25:46Z"
    assert channel_values[0].values[0].value == 307
    assert channel_values[0].values[1].time == "2024-02-01T11:30:00Z"
    assert channel_values[0].values[1].value == 309

    # check latest_value equals values[1]
    assert channel_values[0].latest_value().time == "2024-02-01T11:30:00Z"
    assert channel_values[0].latest_value().value == 309


def test_from_dict_valid_dict_no_values():
    """Test that ChannelValues.from_dict() parses a valid dict correctly even if there are no values."""

    # prepare dict
    channel_values_dict = {
        "channelId": "TheChannelId",
        "componentId": "The:Component-Id",
        "values": [],
    }

    # call from_dict()
    channel_values = ChannelValues.from_dict(channel_values_dict)

    # check result
    assert len(channel_values) == 1

    assert channel_values[0].channel_id == "TheChannelId"
    assert channel_values[0].component_id == "The:Component-Id"

    with pytest.raises(ValueError):
        channel_values[0].latest_value()


def test_from_dict_valid_dict_array_channel():
    """Test that ChannelValues.from_dict() parses a valid dict correctly even if it is for a array channel."""
    # prepare dict
    channel_values_dict = {
        "channelId": "TheChannelId[]",
        "componentId": "The:Component-Id",
        "values": [
            {"time": "2024-02-01T11:25:46Z", "values": [10, 20]},
        ],
    }

    # call from_dict()
    channel_values = ChannelValues.from_dict(channel_values_dict)

    # check result
    assert len(channel_values) == 2

    assert channel_values[0].channel_id == "TheChannelId[0]"
    assert channel_values[0].component_id == "The:Component-Id"
    assert channel_values[0].values[0].time == "2024-02-01T11:25:46Z"
    assert channel_values[0].values[0].value == 10

    assert channel_values[1].channel_id == "TheChannelId[1]"
    assert channel_values[1].component_id == "The:Component-Id"
    assert channel_values[1].values[0].time == "2024-02-01T11:25:46Z"
    assert channel_values[1].values[0].value == 20


def test_from_dict_invalid_dict():
    """Test that ChannelValues.from_dict() raises an exception if the dict is invalid."""

    with pytest.raises(SMAApiParsingError):
        ChannelValues.from_dict({})
