"""Test sma-ennexos coordinator component."""

from unittest.mock import MagicMock

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sma_ennexos.const import DOMAIN
from custom_components.sma_ennexos.coordinator import SMADataCoordinator
from custom_components.sma_ennexos.sma.client import SMAApiClient


async def test_coordinator_basic(
    anyio_backend,
    hass,
    bypass_integration_setup,
    mock_sma_client,
):
    """Test the basic functionality of the coordinator."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test",
        data={},
    )

    # create the coordinator
    coordinator = SMADataCoordinator(
        hass,
        config_entry=entry,
        client=SMAApiClient(
            host="sma.local", username="user", password="password", session=MagicMock()
        ),
    )

    mock_sma_client.reset_counts()
    mock_sma_client.measurements = MagicMock()

    # fetch the data for the first time
    data = await coordinator._async_update_data()
    assert data
    assert data == mock_sma_client.measurements

    # the api client was logged in and called once to fetch the data
    assert mock_sma_client.cnt_login == 1
    assert mock_sma_client.cnt_get_live_measurements == 1
