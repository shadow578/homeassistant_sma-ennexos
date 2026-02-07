"""Configure pytest for all tests."""

from collections.abc import Callable
from unittest import mock
from unittest.mock import patch

import pytest
from attr import dataclass

from custom_components.sma_ennexos.sma.client import LoginResult
from custom_components.sma_ennexos.sma.known_channels import KnownChannelEntry
from custom_components.sma_ennexos.sma.model import (
    ChannelValues,
    ComponentInfo,
    LiveMeasurementQueryItem,
)

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


@dataclass
class MockSmaClientHandle:
    """Call counts for mock_sma_client."""

    cnt_login: int = 0
    cnt_logout: int = 0
    cnt_get_all_components: int = 0
    cnt_get_all_live_measurements: int = 0
    cnt_get_live_measurements: int = 0
    cnt_get_localizations: int = 0

    def reset_counts(self):
        """Reset all call counts to zero."""
        self.cnt_login = 0
        self.cnt_logout = 0
        self.cnt_get_all_components = 0
        self.cnt_get_all_live_measurements = 0
        self.cnt_get_live_measurements = 0
        self.cnt_get_localizations = 0

    # return value for get_all_components
    components: list[ComponentInfo] = []

    # return value for get_all_live_measurements and get_live_measurements
    measurements: list[ChannelValues] = []

    # return value for get_localizations
    localizations: list[tuple[str, dict]] = []

    # additional hooks
    on_login: Callable | None = None
    on_logout: Callable | None = None
    on_get_all_components: Callable | None = None
    on_get_all_live_measurements: Callable[[list[str]], None] | None = None
    on_get_live_measurements: (
        Callable[[list[LiveMeasurementQueryItem]], None] | None
    ) = None
    on_get_localizations: Callable | None = None


@pytest.fixture()
def mock_sma_client():
    """Fixture to mock SMA ennexOS api client function calls."""

    hnd = MockSmaClientHandle()

    async def login():
        nonlocal hnd
        if hnd.on_login:
            hnd.on_login()
        hnd.cnt_login += 1
        return LoginResult.ALREADY_LOGGED_IN

    async def logout():
        nonlocal hnd
        if hnd.on_logout:
            hnd.on_logout()
        hnd.cnt_logout += 1

    async def get_all_components():
        nonlocal hnd
        if hnd.on_get_all_components:
            hnd.on_get_all_components()
        hnd.cnt_get_all_components += 1
        return hnd.components

    async def get_all_live_measurements(component_ids: list[str]):
        nonlocal hnd
        if hnd.on_get_all_live_measurements:
            hnd.on_get_all_live_measurements(component_ids)
        hnd.cnt_get_all_live_measurements += 1
        return hnd.measurements

    async def get_live_measurements(query: list[LiveMeasurementQueryItem]):
        nonlocal hnd
        if hnd.on_get_live_measurements:
            hnd.on_get_live_measurements(query)
        hnd.cnt_get_live_measurements += 1
        return hnd.measurements

    async def get_localizations():
        nonlocal hnd
        if hnd.on_get_localizations:
            hnd.on_get_localizations()
        hnd.cnt_get_localizations += 1
        return hnd.localizations

    with (
        mock.patch(
            "custom_components.sma_ennexos.sma.client.SMAApiClient.login", wraps=login
        ),
        mock.patch(
            "custom_components.sma_ennexos.sma.client.SMAApiClient.logout", wraps=logout
        ),
        mock.patch(
            "custom_components.sma_ennexos.sma.client.SMAApiClient.get_all_components",
            wraps=get_all_components,
        ),
        mock.patch(
            "custom_components.sma_ennexos.sma.client.SMAApiClient.get_all_live_measurements",
            wraps=get_all_live_measurements,
        ),
        mock.patch(
            "custom_components.sma_ennexos.sma.client.SMAApiClient.get_live_measurements",
            wraps=get_live_measurements,
        ),
        mock.patch(
            "custom_components.sma_ennexos.sma.client.SMAApiClient.get_localizations",
            wraps=get_localizations,
        ),
    ):
        yield hnd


@pytest.fixture()
def mock_known_channels():
    """Fixture to mock known_channels in sensor platform."""

    known_channels: dict[str, KnownChannelEntry] = {}

    def get_known_channel(channel_id: str) -> KnownChannelEntry | None:
        nonlocal known_channels
        return known_channels.get(channel_id)

    with mock.patch(
        # have to patch the importing module, not the defining module
        "custom_components.sma_ennexos.sensor.get_known_channel",
        wraps=get_known_channel,
    ) as m:
        yield (m, known_channels)
