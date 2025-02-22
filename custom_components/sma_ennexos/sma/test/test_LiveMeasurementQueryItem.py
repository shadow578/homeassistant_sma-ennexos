"""unit tests for model.LiveMeasurementQueryItem."""

from ..model import LiveMeasurementQueryItem

def test_to_dict():
    """Test that LiveMeasurementQueryItem.to_dict() returns the correct dict."""

    # prepare LiveMeasurementQueryItem
    query = LiveMeasurementQueryItem(
        component_id="The:Component-Id",
        channel_id="TheChannelId",
    )

    # call to_dict()
    query_dict = query.to_dict()

    # check result
    assert query_dict == {
        "componentId": "The:Component-Id",
        "channelId": "TheChannelId",
    }
