"""Validate localization files."""

import json
from os import path

from custom_components.sma_ennexos.sma.known_channels import __KNOWN_CHANNELS
from custom_components.sma_ennexos.util import channel_to_translation_key


def assert_channel_translation_keys_present(file_path: str):
    """Check if all channels in known_channels have a matching translation key."""
    with open(file_path) as f:
        translations = json.load(f)

    assert translations is not None and isinstance(translations, dict)
    assert translations["entity"] is not None and isinstance(
        translations["entity"], dict
    )
    assert translations["entity"]["sensor"] is not None and isinstance(
        translations["entity"]["sensor"], dict
    )

    translations = translations["entity"]["sensor"]

    for channel_id in __KNOWN_CHANNELS:
        translation_key = channel_to_translation_key(channel_id)

        # ensure translation key is present
        entry = translations.get(translation_key)
        assert entry is not None, (
            f"No translation for channel '{channel_id}' (translation_key='{translation_key}')"
        )
        assert isinstance(entry, dict), (
            f"Invalid translation for channel '{channel_id}' (translation_key='{translation_key}')"
        )

        # should have a "name" localization
        name = entry.get("name")
        assert name is not None, (
            f"Missing entity name translation for channel '{channel_id}' (translation_key='{translation_key}')"
        )
        assert isinstance(name, str), (
            f"Entity name translation for channel '{channel_id}' was not a string (translation_key='{translation_key}')"
        )
        assert name != "", (
            f"Entity name translation for channel '{channel_id}' is empty (translation_key='{translation_key}')"
        )


def test_translation_keys_present_en():
    """Ensure translation is present for english language."""
    assert_channel_translation_keys_present(
        path.join(".", "custom_components", "sma_ennexos", "translations", "en.json")
    )


def test_translation_keys_present_de():
    """Ensure translation is present for german language."""
    assert_channel_translation_keys_present(
        path.join(".", "custom_components", "sma_ennexos", "translations", "de.json")
    )
