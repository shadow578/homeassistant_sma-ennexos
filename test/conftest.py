"""Configure pytest for all tests."""

from unittest.mock import patch

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture()
def hass(hass, enable_custom_integrations):
    """Return a Home Assistant instance that can load custom integrations."""
    yield hass


@pytest.fixture()
def anyio_backend():
    """Define the 'anyio_backend' fixture for asyncio.

    see https://anyio.readthedocs.io/en/stable/testing.html
    """
    return "asyncio"


@pytest.fixture()
def bypass_integration_setup():
    """Fixture to replace 'async_setup_entry' with a mock."""
    with (
        patch("custom_components.sma_ennexos.async_setup_entry", return_value=True),
        patch(
            "custom_components.sma_ennexos.async_unload_entry", return_value=True
        ) as mock,
    ):
        yield mock
