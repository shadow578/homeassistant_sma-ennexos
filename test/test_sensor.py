"""Test sma-ennexos sensor component."""

from unittest import mock

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers import device_registry, entity_registry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sma_ennexos.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEVICE_MANUFACTURER,
    DOMAIN,
)
from custom_components.sma_ennexos.sma.known_channels import (
    KnownChannelEntry,
    SMACumulativeMode,
    SMADeviceKind,
    SMAUnit,
)
from custom_components.sma_ennexos.sma.model import (
    ChannelValues,
    ComponentInfo,
    LiveMeasurementQueryItem,
    TimeValuePair,
)


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


async def test_sensor_basic(
    anyio_backend,
    hass,
    mock_sma_client,
    mock_known_channels,
):
    """Test basic sensor setup and function."""
    _, known_channels = mock_known_channels

    mock_sma_client.components = [
        ComponentInfo(
            component_id="component1",
            component_type="type1",
            name="Component 1",
        ),
        ComponentInfo(
            component_id="component2",
            component_type="type2",
            name="Component 2",
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

    known_channels["channel1"] = known_channels["channel2"] = KnownChannelEntry(
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT,
    )

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
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # following sensors should be present
    state = hass.states.get("sensor.component_1_channel1")
    assert state
    assert state.state == "300.0"

    state = hass.states.get("sensor.component_2_channel2")
    assert state
    assert state.state == "400.0"


async def test_sensor_known_channel_attributes(
    anyio_backend,
    hass,
    mock_sma_client,
    mock_known_channels,
):
    """Test sensor state attributes are applied from known_channels."""
    get_known_channels_fn, known_channels = mock_known_channels

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

    known_channels["Mock.Measurement.TotWhOut"] = KnownChannelEntry(
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT_HOUR,
        cumulative_mode=SMACumulativeMode.TOTAL,
    )

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
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # sensour should have attemptet to figure out a known channel
    assert get_known_channels_fn.called

    # the sensor created should be a energy (Wh) sensor with following attributes
    state = hass.states.get("sensor.mock_inverter_mock_measurement_totwhout")
    assert state
    assert state.state == "300.0"

    # from CUMULATIVE_MODE_TOTAL
    assert state.attributes["state_class"] == SensorStateClass.TOTAL_INCREASING

    # from UNIT_WATT_HOUR
    assert state.attributes["unit_of_measurement"] == "Wh"
    assert state.attributes["device_class"] == SensorDeviceClass.ENERGY


async def test_sensor_known_channel_enum(
    anyio_backend,
    hass,
    mock_sma_client,
):
    """Test enum sensors set state and attributes correctly."""
    with mock.patch(
        # note: need to patch in the importing module, not the defining module
        "custom_components.sma_ennexos.sensor.get_known_channel"
    ) as mock_get_known_channel:
        mock_get_known_channel.return_value = KnownChannelEntry(
            device_kind=SMADeviceKind.OTHER,
            unit=SMAUnit.ENUM,
            enum_values={
                0: "mock-enum-0",
                10: "mock-enum-10",
            },
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
                channel_id="Mock.Measurement.Operation.Health",
                values=[
                    TimeValuePair(
                        time="2024-02-01T11:25:46Z",
                        value=10,
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
        )
        config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        # sensour should have attemptet to figure out a known channel
        assert mock_get_known_channel.called

        # the sensor created should be a energy (Wh) sensor with following attributes
        state = hass.states.get(
            "sensor.mock_inverter_mock_measurement_operation_health"
        )
        assert state
        assert state.state == "mock-enum-10"

        # enum sensors have no state class and no unit
        assert state.attributes.get("state_class") is None
        assert state.attributes.get("unit_of_measurement") is None
        assert state.attributes["device_class"] == SensorDeviceClass.ENUM

        # options is set to a list of possible enum values
        assert state.attributes["options"] == ["mock-enum-0", "mock-enum-10"]


async def test_sensor_none_value_fallback(
    anyio_backend,
    hass,
    mock_sma_client,
    mock_known_channels,
):
    """Test sensor handles None value according to known_channels."""
    get_known_channel_fn, known_channels = mock_known_channels

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
            channel_id="Mock.Measurement.TotW.Pv",
            values=[
                TimeValuePair(
                    time="2024-02-01T11:25:46Z",
                    value=None,  # e.g. when inverter is in standby
                )
            ],
        )
    ]

    known_channels["Mock.Measurement.TotW.Pv"] = KnownChannelEntry(
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT,
        value_when_none=0,
    )

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
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # sensour should have attemptet to figure out a known channel
    assert get_known_channel_fn.called

    # the sensor created should be a power (W) sensor at 0W (value_when_none=0)
    state = hass.states.get("sensor.mock_inverter_mock_measurement_totw_pv")
    assert state
    assert state.state == "0"

    # no cumulative mode
    assert state.attributes["state_class"] == SensorStateClass.MEASUREMENT

    # from UNIT_WATT
    assert state.attributes["unit_of_measurement"] == "W"
    assert state.attributes["device_class"] == SensorDeviceClass.POWER


async def test_device_entries(
    anyio_backend,
    hass,
    mock_sma_client,
    mock_known_channels,
):
    """Test device entries are created for every component."""
    _, known_channels = mock_known_channels

    mock_sma_client.components = [
        ComponentInfo(
            component_id="component1",
            component_type="type1",
            name="Component 1",
        ),
        ComponentInfo(
            component_id="component2",
            component_type="type2",
            name="Component 2",
            vendor="Vendor Name",
            product_name="Model Name",
            serial_number="123456",
            firmware_version="1.2.3",
            ip_address="127.0.0.2",
            generator_power=2345,
            product_tag_id=8765,
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

    known_channels["channel1"] = known_channels["channel2"] = KnownChannelEntry(
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT,
    )

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
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)

    # get device entry for component1 channel1
    entity = er.async_get("sensor.component_1_channel1")
    assert entity is not None
    assert entity.device_id is not None

    device = dr.async_get(entity.device_id)
    assert device is not None

    assert device.name == "Component 1"

    assert device.manufacturer == DEVICE_MANUFACTURER
    assert device.model is None
    assert device.serial_number is None
    assert device.sw_version is None
    assert device.configuration_url is None

    # get device entry for component2 channel2
    entity = er.async_get("sensor.component_2_channel2")
    assert entity is not None
    assert entity.device_id is not None

    device = dr.async_get(entity.device_id)
    assert device is not None

    assert device.name == "Component 2"

    assert device.manufacturer == "Vendor Name"
    assert device.model == "Model Name"
    assert device.serial_number == "123456"
    assert device.sw_version == "1.2.3"
    assert device.configuration_url == "https://127.0.0.2/"


async def test_sensor_disabled_entities_are_not_fetched(
    anyio_backend,
    hass,
    mock_sma_client,
    mock_known_channels,
):
    """Test that entities that are disabled in the entity registry are not fetched."""
    _, known_channels = mock_known_channels

    mock_sma_client.components = [
        ComponentInfo(
            component_id="component1",
            component_type="type1",
            name="Component 1",
        ),
        ComponentInfo(
            component_id="component2",
            component_type="type2",
            name="Component 2",
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

    known_channels["channel1"] = known_channels["channel2"] = KnownChannelEntry(
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT,
    )

    # add a hook to record the query used in get_live_measurements call
    last_query: list[LiveMeasurementQueryItem] = []

    def on_get_live_measurements(query: list[LiveMeasurementQueryItem]):
        nonlocal last_query
        last_query = query

    mock_sma_client.on_get_live_measurements = on_get_live_measurements

    # setup the entry
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
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # following sensors should be present
    state = hass.states.get("sensor.component_1_channel1")
    assert state
    assert state.state == "300.0"

    state = hass.states.get("sensor.component_2_channel2")
    assert state
    assert state.state == "400.0"

    # should have queried for both channels
    assert len(last_query) == 2
    assert last_query[0].component_id == "component1"
    assert last_query[0].channel_id == "channel1"
    assert last_query[1].component_id == "component2"
    assert last_query[1].channel_id == "channel2"

    # disable the first sensor
    er = entity_registry.async_get(hass)
    er.async_update_entity(
        "sensor.component_1_channel1",
        disabled_by=entity_registry.RegistryEntryDisabler.USER,
    )

    # should no longer have a state, it's disabled
    state = hass.states.get("sensor.component_1_channel1")
    assert state is None

    # change the values for both channels, to see if updates go trough
    mock_sma_client.measurements[0].values[0].value = 301.0
    mock_sma_client.measurements[1].values[0].value = 401.0

    # force refresh the coordinator to fetch new values
    await hass.data[DOMAIN][config_entry.entry_id].async_refresh()
    await hass.async_block_till_done()

    # channel 1 should still be disabled
    state = hass.states.get("sensor.component_1_channel1")
    assert state is None

    # channel 2 should have updated value
    state = hass.states.get("sensor.component_2_channel2")
    assert state
    assert state.state == "401.0"

    # should have queried only for the enabled channel
    assert len(last_query) == 1
    assert last_query[0].component_id == "component2"
    assert last_query[0].channel_id == "channel2"


async def test_sensor_known_channel_enabled_by_default(
    anyio_backend,
    hass,
    mock_sma_client,
    mock_known_channels,
):
    """Test that sensors for channels present in known_channels are enabled by default."""
    _, known_channels = mock_known_channels

    mock_sma_client.components = [
        ComponentInfo(
            component_id="component1",
            component_type="type1",
            name="Component 1",
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
    ]

    known_channels["channel1"] = KnownChannelEntry(
        device_kind=SMADeviceKind.PV,
        unit=SMAUnit.WATT,
    )

    # setup the entry
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
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # sensor is enabled, thus should have a state
    state = hass.states.get("sensor.component_1_channel1")
    assert state
    assert state.state == "300.0"

    # querying from the entity registry should show the entity is enabled
    er = entity_registry.async_get(hass)
    entry = er.async_get("sensor.component_1_channel1")
    assert entry
    assert entry.disabled_by is None


async def test_sensor_unknown_channels_disabled_by_default(
    anyio_backend,
    hass,
    mock_sma_client,
    mock_known_channels,
):
    """Test that sensors for channels not present in known_channels are disabled by default."""
    _, known_channels = mock_known_channels

    mock_sma_client.components = [
        ComponentInfo(
            component_id="component1",
            component_type="type1",
            name="Component 1",
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
    ]

    known_channels["channel1"] = None  # unknown channel

    # setup the entry
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
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # sensor is disabled, thus should have no state
    state = hass.states.get("sensor.component_1_channel1")
    assert state is None

    # querying from the entity registry should show the entity is disabled by the integration
    er = entity_registry.async_get(hass)
    entry = er.async_get("sensor.component_1_channel1")
    assert entry
    assert entry.disabled_by is entity_registry.RegistryEntryDisabler.INTEGRATION
