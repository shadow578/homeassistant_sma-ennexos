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


def channel_fqid_to_parts(fqid: str) -> tuple[str, str]:
    """Convert a channel fqid (channel@component) to its component_id and channel_id parts.

    :param fqid: The channel fqid to convert (channel@component).
    :return: a tuple of (component_id, channel_id)
    """
    split = fqid.split("@")

    if len(split) != 2:
        raise ValueError(f"Invalid channel fqid: {fqid}")

    return (split[1], split[0])


def channel_parts_to_entity_id(component_id: str, channel_id: str, kind: str) -> str:
    """Convert a channel_id and component_id to an entity id.

    :param component_id: The component_id of the channel.
    :param channel_id: The channel_id of the channel.
    :param kind: The kind of entity. e.g. sensor, binary_sensor, etc.
    :return: entity id
    """

    # transform array index to be just a suffix
    if channel_id.endswith("]"):
        channel_id = channel_id.replace("[", "_").replace("]", "")

    # concat component and channel id
    s = f"{component_id}_{channel_id}"

    # lower case
    s = s.lower()

    # replace "delimiting characters" and spaces with underscores
    for c in " -.:":
        s = s.replace(c, "_")

    # remove all non-alphanumeric characters except underscores
    s = "".join(c if c.isalnum() or c == "_" else "" for c in s)

    # trim underscores from start and end
    s = s.strip("_")

    # remove all occurrences of multiple underscores
    while "__" in s:
        s = s.replace("__", "_")

    return f"{kind}.{s}"
