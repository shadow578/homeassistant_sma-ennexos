"""integration utilities."""


def __normalize_for_id(s: str) -> str:
    """Normalize a string for use in an entity id or translation key."""
    # lower case
    s = s.lower()

    # replace "delimiting characters" and spaces with underscores
    for c in " -.:":
        s = s.replace(c, "_")

    # replace umlauts with ascii equivalents
    UMLAUT_REPLACEMENTS = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
    }
    for umlaut, replacement in UMLAUT_REPLACEMENTS.items():
        s = s.replace(umlaut, replacement)

    # filter to only allow allowed characters (a-z, 0-9, and underscore)
    def is_allowed_char(c: str) -> bool:
        return c.isnumeric() or (c.isalpha() and c >= "a" and c <= "z") or c == "_"

    s = "".join(c if is_allowed_char(c) else "" for c in s)

    # trim underscores from start and end
    s = s.strip("_")

    # remove all occurrences of multiple underscores
    while "__" in s:
        s = s.replace("__", "_")

    return s


def channel_parts_to_entity_id(component_name: str, channel_id: str, kind: str) -> str:
    """
    Convert a channel_id and component_id to an entity id.

    :param component_name: The name or id of the component.
    :param channel_id: The channel_id of the channel.
    :param kind: The kind of entity. e.g. sensor, binary_sensor, etc.
    :return: entity id
    """
    # transform array index to be just a suffix
    if channel_id.endswith("]"):
        channel_id = channel_id.replace("[", "_").replace("]", "")

    # concat component and channel id
    s = f"{component_name}_{channel_id}"

    s = __normalize_for_id(s)
    return f"{kind}.{s}"


def channel_to_translation_key(channel_id: str) -> str:
    """
    Convert a channel_id to a translation key.

    :param channel_id: The channel_id of the channel.
    :return: translation key
    """
    # remove array index
    if channel_id.endswith("]"):
        bracket_start = channel_id.rfind("[")
        channel_id = f"{channel_id[0:bracket_start]}"

    return __normalize_for_id(channel_id)
