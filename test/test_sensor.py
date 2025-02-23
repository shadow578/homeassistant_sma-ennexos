"""Test sma-ennexos sensor component."""

from unittest import mock

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers import device_registry, entity_registry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sma_ennexos import async_setup_entry
from custom_components.sma_ennexos.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEVICE_MANUFACTURER,
    DOMAIN,
    OPT_SENSOR_CHANNELS,
)
from custom_components.sma_ennexos.sma.known_channels import (
    CUMULATIVE_MODE_TOTAL,
    DEVICE_KIND_PV,
    UNIT_WATT_HOUR,
    KnownChannelEntry,
)
from custom_components.sma_ennexos.sma.model import (
    ChannelValues,
    ComponentInfo,
    TimeValuePair,
)
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

    # following sensors should be present
    state = hass.states.get("sensor.component1_channel1")
    assert state
    assert state.state == "300.0"

    state = hass.states.get("sensor.component2_channel2")
    assert state
    assert state.state == "400.0"


async def test_sensor_known_channel_attributes(
    anyio_backend,
    hass,
    mock_sma_client,
):
    """Test sensor state attributes are applied from known_channels."""
    with mock.patch(
        # note: need to patch in the importing module, not the defining module
        "custom_components.sma_ennexos.sensor.get_known_channel"
    ) as mock_get_known_channel:
        mock_get_known_channel.return_value = KnownChannelEntry(
            name="MOCK TotWhOut",
            device_kind=DEVICE_KIND_PV,
            unit=UNIT_WATT_HOUR,
            cumulative_mode=CUMULATIVE_MODE_TOTAL,
        )

        mock_sma_client.components = [
            ComponentInfo(
                component_id="mock_inverter",
                component_type="Inverter",
                name="Mock Inverter",
            )
        ]

        mock_sma_client.measurements = [
            ChannelValues(
                component_id="mock_inverter",
                channel_id="Mock.Measurement.TotWhOut",
                values=[
                    TimeValuePair(
                        time="2024-02-01T11:25:46Z",
                        value=300.0,
                    )
                ],
            )
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
                OPT_SENSOR_CHANNELS: [channel_parts_to_fqid("mock_inverter", "Mock.Measurement.TotWhOut")]
            },
        )
        config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        assert await async_setup_entry(hass, config_entry)
        await hass.async_block_till_done()

        # sensour should have attemptet to figure out a known channel
        assert mock_get_known_channel.called

        # the sensor created should be a energy (Wh) sensor with following attributes
        state = hass.states.get("sensor.mock_inverter_mock_measurement_totwhout")
        assert state
        assert state.state == "300.0"

        # from CUMULATIVE_MODE_TOTAL
        assert state.attributes["state_class"] == SensorStateClass.TOTAL_INCREASING

        # from UNIT_WATT_HOUR
        assert state.attributes["unit_of_measurement"] == "Wh"
        assert state.attributes["device_class"] == SensorDeviceClass.ENERGY


async def test_device_entries(
    anyio_backend,
    hass,
    mock_sma_client,
):
    """Test device entries are created for every component."""
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
            serial_number="123456",
            firmware_version="1.2.3",
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

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)

    # get device entry for component1 channel1
    entity = er.async_get("sensor.component1_channel1")
    assert entity is not None
    assert entity.device_id is not None

    device = dr.async_get(entity.device_id)
    assert device is not None

    assert device.name == "Component 1 Name"
    assert device.manufacturer == DEVICE_MANUFACTURER
    assert device.model is None  # no model
    assert device.sw_version is None  # no firmware version

    # get device entry for component2 channel2
    entity = er.async_get("sensor.component2_channel2")
    assert entity is not None
    assert entity.device_id is not None

    device = dr.async_get(entity.device_id)
    assert device is not None

    assert device.name == "Component 2 Name"
    assert device.manufacturer == DEVICE_MANUFACTURER
    assert device.model == "123456"
    assert device.sw_version == "1.2.3"
