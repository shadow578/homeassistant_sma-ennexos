"""Test sma-ennexos config and option flow."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sma_ennexos.config_flow import OPT_ALL_SENSOR_CHANNELS
from custom_components.sma_ennexos.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DOMAIN,
    OPT_REQUEST_RETIRES,
    OPT_REQUEST_TIMEOUT,
    OPT_SENSOR_CHANNELS,
    OPT_UPDATE_INTERVAL,
)
from custom_components.sma_ennexos.sma.model import (
    ChannelValues,
    ComponentInfo,
    SMAApiAuthenticationError,
    TimeValuePair,
)
from custom_components.sma_ennexos.util import channel_parts_to_fqid


# note: need to bypass integration setup since otherwise it would interfere with the
# counters for mock_sma_client
async def test_config_flow_user_step_ok(
    anyio_backend, hass, bypass_integration_setup, mock_sma_client
):
    """Test that the 'user' config step correctly creates an configuration entry."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    # first step is a form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # ensure plant name is returned as "MOCK PLANT"
    # the plant component is the first component returned
    # by get_all_components with type=Plant
    mock_sma_client.components = [
        ComponentInfo(
            component_id="plant",
            component_type="Plant",
            name="MOCK PLANT",
        )
    ]

    mock_sma_client.reset_counts()

    # if a user were to enter host=sma.local, username=user, password=pass, use_ssl=True, verify_ssl=True,
    # this call would be dispatched.
    # behind the scenes, the config flow should verify the credentials, and then create a config entry.
    # the title of the config entry is the plant name
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "sma.local",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_USE_SSL: True,
            CONF_VERIFY_SSL: True,
        },
    )

    # to check the connection and fetch the plant name, a call
    # to the api should have happened
    assert mock_sma_client.cnt_login == 1
    assert mock_sma_client.cnt_get_all_components == 1

    # a new config entry should have been created
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "MOCK PLANT"
    assert result["data"] == {
        CONF_HOST: "sma.local",
        CONF_USERNAME: "user",
        CONF_PASSWORD: "pass",
        CONF_USE_SSL: True,
        CONF_VERIFY_SSL: True,
    }
    assert result["options"] == {}  # no options yet
    assert result["result"]


async def test_config_flow_user_step_handles_invalid_auth(
    anyio_backend, hass, bypass_integration_setup, mock_sma_client
):
    """Test that the 'user' config step correctly handles auth errors when verifying the connection."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    # first step is a form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    mock_sma_client.reset_counts()

    # simulate a call with invalid credentials by hooking login() to raise an exception
    def on_login():
        raise SMAApiAuthenticationError("simulated invalid credentials")

    mock_sma_client.on_login = on_login

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "sma.local",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_USE_SSL: True,
            CONF_VERIFY_SSL: True,
        },
    )

    # because login failed, no call to get_all_components happened
    # login is irrelevant as it's hooked
    assert mock_sma_client.cnt_get_all_components == 0

    # no config entry is created
    # instead, a form is returned with a error message
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "auth_fail"}  # auth error


async def test_config_flow_user_step_handles_no_plant(
    anyio_backend, hass, bypass_integration_setup, mock_sma_client
):
    """Test that the 'user' config step correctly handles no plant returned by the API."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    # first step is a form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    mock_sma_client.reset_counts()

    # simulate a misbehaving API by returning no components
    mock_sma_client.components = []

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "sma.local",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_USE_SSL: True,
            CONF_VERIFY_SSL: True,
        },
    )

    # no config entry is created
    # instead, a form is returned with a error message
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "no_plant_component"}


async def test_options_flow_init_step_ok(
    anyio_backend, hass, bypass_integration_setup, mock_sma_client
):
    """Test that the 'init' options step correctly creates an options entry."""

    # create a config entry to bypass the config flow
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "sma.local",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_USE_SSL: True,
            CONF_VERIFY_SSL: True,
        },
    )
    entry.add_to_hass(hass)

    # ensure there are some components returned by the API
    mock_sma_client.components = [
        ComponentInfo(
            component_id="plant",
            component_type="Plant",
            name="MOCK PLANT",
        ),
        ComponentInfo(
            component_id="inverter1",
            component_type="Inverter",
            name="MOCK INVERTER",
        ),
    ]
    mock_sma_client.measurements = [
        ChannelValues(
            channel_id="volt",
            component_id="inverter1",
            values=[TimeValuePair(time="2021-01-01T12:00:00Z", value=230.0)],
        )
    ]

    mock_sma_client.reset_counts()

    # initialize options flow
    await hass.config_entries.async_setup(entry.entry_id)
    result = await hass.config_entries.options.async_init(entry.entry_id)

    # first step is a form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # TODO verify the multi select contains the correct options

    # already, there should have been a call to get_all_components
    assert mock_sma_client.cnt_get_all_components == 1

    mock_sma_client.reset_counts()

    # simulate user selecting some options
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            OPT_SENSOR_CHANNELS: [
                channel_parts_to_fqid("inverter1", "volt"),
            ],
            OPT_UPDATE_INTERVAL: 30,
            OPT_REQUEST_TIMEOUT: 10,
            OPT_REQUEST_RETIRES: 3,
        },
    )

    # the flow should now finish and create a options entry
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        OPT_SENSOR_CHANNELS: [
            channel_parts_to_fqid("inverter1", "volt"),
        ],
        OPT_UPDATE_INTERVAL: 30,
        OPT_REQUEST_TIMEOUT: 10,
        OPT_REQUEST_RETIRES: 3,
    }


async def test_options_flow_init_step_all_channels(
    anyio_backend, hass, bypass_integration_setup, mock_sma_client
):
    """Test that the 'init' options step correctly selects all channels if requested."""

    # create a config entry to bypass the config flow
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "sma.local",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "pass",
            CONF_USE_SSL: True,
            CONF_VERIFY_SSL: True,
        },
    )
    entry.add_to_hass(hass)

    # ensure there are some components returned by the API
    mock_sma_client.components = [
        ComponentInfo(
            component_id="plant",
            component_type="Plant",
            name="MOCK PLANT",
        ),
        ComponentInfo(
            component_id="inverter1",
            component_type="Inverter",
            name="MOCK INVERTER",
        ),
    ]
    mock_sma_client.measurements = [
        ChannelValues(
            channel_id="volt",
            component_id="inverter1",
            values=[TimeValuePair(time="2021-01-01T12:00:00Z", value=230.0)],
        ),
        ChannelValues(
            channel_id="amp",
            component_id="inverter1",
            values=[TimeValuePair(time="2021-01-01T12:00:00Z", value=10.0)],
        ),
    ]

    mock_sma_client.reset_counts()

    # initialize options flow
    await hass.config_entries.async_setup(entry.entry_id)
    result = await hass.config_entries.options.async_init(entry.entry_id)

    # first step is a form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    mock_sma_client.reset_counts()

    # simulate user selecting "use all channels"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            OPT_SENSOR_CHANNELS: [],
            OPT_ALL_SENSOR_CHANNELS: True,
            OPT_UPDATE_INTERVAL: 30,
            OPT_REQUEST_TIMEOUT: 10,
            OPT_REQUEST_RETIRES: 3,
        },
    )

    # the flow should now finish and create a options entry
    # OPT_SENSOR_CHANNELS should contain all channels, despite
    # the user not selecting any in the dropdown
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]

    channels = result["data"][OPT_SENSOR_CHANNELS]
    assert len(channels) == 2
