"""Test sma_ennexos setup process."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sma_ennexos import (
    async_reload_entry,
    async_unload_entry,
)
from custom_components.sma_ennexos.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DOMAIN,
)
from custom_components.sma_ennexos.coordinator import SMADataCoordinator


async def test_setup_unload_and_reload_entry(anyio_backend, hass, mock_sma_client):
    """Test entry setup, unload and reload."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "sma.local",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "password",
            CONF_USE_SSL: False,
            CONF_VERIFY_SSL: False,
        },
        entry_id="MOCK",
    )
    config_entry.add_to_hass(hass)

    def assert_entry():
        assert DOMAIN in hass.data
        assert config_entry.entry_id in hass.data[DOMAIN]

        entry = hass.data[DOMAIN][config_entry.entry_id]
        assert isinstance(entry, SMADataCoordinator)
        assert entry is not None

    mock_sma_client.reset_counts()

    # setup the entry
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert_entry()

    # should have logged in three times (get_all_components in sensor.py and 2x coordinator refresh)
    # and fetched all components
    assert mock_sma_client.cnt_login == 3
    assert mock_sma_client.cnt_get_all_components == 1

    mock_sma_client.reset_counts()

    # reload the entry and check the data is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert_entry()

    # should have logged out, then re-setup
    assert mock_sma_client.cnt_logout == 1
    assert mock_sma_client.cnt_login == 3
    assert mock_sma_client.cnt_get_all_components == 1

    mock_sma_client.reset_counts()

    # unload the entry and check the data is gone
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]

    # client should have been logged out, but not logged in again
    assert mock_sma_client.cnt_logout == 1
    assert mock_sma_client.cnt_login == 0
