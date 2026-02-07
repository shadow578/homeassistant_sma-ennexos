"""Test SMA ennexOS diagnostics."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sma_ennexos.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DOMAIN,
)
from custom_components.sma_ennexos.diagnostics import async_get_config_entry_diagnostics
from custom_components.sma_ennexos.sma.known_channels import (
    KnownChannelEntry,
    SMADeviceKind,
    SMAUnit,
)
from custom_components.sma_ennexos.sma.model import (
    ChannelValues,
    ComponentInfo,
    TimeValuePair,
)


async def test_diagnostics(
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
            vendor="Vendor",
            product_name="Product",
            firmware_version="1.0",
            serial_number="123456",
            ip_address="192.168.0.10",
            generator_power=1000,
            product_tag_id=5678,
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

    mock_sma_client.localizations = [
        ("en.json", {"greeting": "Hello"}),
        ("de.json", {"greeting": "Hallo"}),
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

    diagnostics = await async_get_config_entry_diagnostics(hass, config_entry)

    entry = diagnostics["config_entry"]
    assert entry["data"][CONF_HOST] == "sma.local"
    assert entry["data"][CONF_USERNAME] != "user"  # redacted
    assert entry["data"][CONF_PASSWORD] != "password"  # redacted
    assert entry["data"][CONF_USE_SSL] is False
    assert entry["data"][CONF_VERIFY_SSL] is True
    assert entry["options"] == {}

    entities = diagnostics["entities"]
    assert len(entities) == 2
    assert (
        entities["sensor.component_1_channel1"].entity_id
        == "sensor.component_1_channel1"
    )
    assert entities["sensor.component_1_channel1"].state == "300.0"

    raw_data = diagnostics["raw_data"]
    assert raw_data["components"] == [
        {
            "component_id": "component1",
            "component_type": "type1",
            "name": "Component 1",
            "vendor": None,
            "product_name": None,
            "serial_number": None,
            "firmware_version": None,
            "ip_address": None,
            "generator_power": None,
            "product_tag_id": None,
        },
        {
            "component_id": "component2",
            "component_type": "type2",
            "name": "Component 2",
            "vendor": "Vendor",
            "product_name": "Product",
            "serial_number": raw_data["components"][1][
                "serial_number"
            ],  # redacted, checked below
            "firmware_version": "1.0",
            "ip_address": "192.168.0.10",
            "generator_power": 1000,
            "product_tag_id": 5678,
        },
    ]
    assert raw_data["components"][1]["serial_number"] != "123456"  # redacted

    assert raw_data["measurements"] == [
        {
            "channel_id": "channel1",
            "component_id": "component1",
            "values": [{"time": "2024-02-01T11:25:46Z", "value": 300.0}],
        },
        {
            "channel_id": "channel2",
            "component_id": "component2",
            "values": [{"time": "2024-02-01T11:25:46Z", "value": 400.0}],
        },
    ]

    assert raw_data["localizations"] == [
        {"filename": "en.json", "lang_data": {"greeting": "Hello"}},
        {"filename": "de.json", "lang_data": {"greeting": "Hallo"}},
    ]
