"""Test sma-ennexos sensor component."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sma_ennexos import async_setup_entry
from custom_components.sma_ennexos.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    OPT_SENSOR_CHANNELS,
    DOMAIN,
)
from custom_components.sma_ennexos.sma.model import ChannelValues, ComponentInfo, TimeValuePair
from custom_components.sma_ennexos.util import channel_parts_to_fqid


async def test_sensor_basic(
    anyio_backend,
    hass,
    mock_sma_client,
):
    """Test basic sensor setup and function."""
    mock_sma_client.components = [
        ComponentInfo(
            component_id="component1",
            component_type="type1",
            name="Component 1 Name",
        ),
        ComponentInfo(
            component_id="component2",
            component_type="type2",
            name="Component 2 Name",
        ),
    ]

    mock_sma_client.measurements = [
        ChannelValues(
            component_id="component1",
            channel_id="channel1",
            values=[
                TimeValuePair(
                    time="2024-02-01T11:25:46Z",
                    value=300.0,
                )
            ],
        ),
        ChannelValues(
            component_id="component2",
            channel_id="channel2",
            values=[
                TimeValuePair(
                    time="2024-02-01T11:25:46Z",
                    value=400.0,
                )
            ],
        ),
    ]

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="MOCK",
        data={
            CONF_HOST: "sma.local",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "password",
            CONF_USE_SSL: False,
            CONF_VERIFY_SSL: True,
        },
        options={
            OPT_SENSOR_CHANNELS: [
                channel_parts_to_fqid("component1", "channel1"),
                channel_parts_to_fqid("component2", "channel2"),
            ]
        },
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # following sensors should be present:
    # - sensor.component_1_channel_1 : 300.0
    # - sensor.component_2_channel_2 : "online"
    state = hass.states.get("sensor.component_1_channel_1")
    assert state
    assert state.state == "300.0"

    state = hass.states.get("sensor.component_2_channel_2")
    assert state
    assert state.state == "400.0"
