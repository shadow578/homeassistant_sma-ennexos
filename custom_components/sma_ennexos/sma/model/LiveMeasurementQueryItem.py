"""Query entry for get_live_measurement."""


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
