"""integration utilities."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .coordinator import SMAUpdateCoordinator
    from .sma.model import ComponentInfo


class SMAEntryData:
    """data stored in domain entry of hass.data."""

    coordinator: "SMAUpdateCoordinator"
    all_components: list["ComponentInfo"]

    def __init__(
        self,
        coordinator: "SMAUpdateCoordinator",
        all_components: list["ComponentInfo"],
    ) -> None:
        """Initialize."""
        self.coordinator = coordinator
        self.all_components = all_components


def channel_parts_to_fqid(component_id: str, channel_id: str) -> str:
    """Convert a channel_id and component_id to a channel fqid (channel@component).

    :param component_id: The component_id of the channel.
    :param channel_id: The channel_id of the channel.
    :return: a channel fqid (channel@component).
    """
    return f"{channel_id}@{component_id}"


def channel_fqid_to_parts(fqid: str) -> (str, str):
    """Convert a channel fqid (channel@component) to its component_id and channel_id parts.

    :param fqid: The channel fqid to convert (channel@component).
    :return: a tuple of (component_id, channel_id)
    """
    split = fqid.split("@")

    if len(split) != 2:
        raise ValueError(f"Invalid channel fqid: {fqid}")

    return (split[1], split[0])
