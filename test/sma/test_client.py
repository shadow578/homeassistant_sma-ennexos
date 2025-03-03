"""unit test for SMA client implementation."""

from typing import Any
from unittest import mock
from urllib.parse import quote

import pytest

from custom_components.sma_ennexos.sma.client import (
    LOGIN_RESULT_ALREADY_LOGGED_IN,
    LOGIN_RESULT_NEW_TOKEN,
    LOGIN_RESULT_TOKEN_REFRESHED,
    SMAApiClient,
)
from custom_components.sma_ennexos.sma.model import LiveMeasurementQueryItem

from .http_response_mock import ClientResponseMock


@pytest.mark.asyncio
async def test_client_auth():
    """Test client login / logout methods."""

    # mock for make_request
    did_get_token = False
    did_refresh_token = False
    did_delete_token = False

    async def make_request_mock(
        method: str,
        endpoint: str,
        data: dict | None = None,
        headers: dict | None = None,
        as_json: bool = True,
    ):
        """Mock for make_request."""
        nonlocal did_get_token
        nonlocal did_refresh_token
        nonlocal did_delete_token

        # POST /api/v1/token (login, NEW and REFRESH)
        if method == "POST" and endpoint == "token":
            assert data is not None
            assert (
                data["grant_type"] == "password"
                or data["grant_type"] == "refresh_token"
            )

            # check headers
            assert headers is not None

            # origin headers
            assert headers["Origin"] == "http://sma.local/api/v1"
            assert headers["Host"] == "sma.local"

            # content type headers
            assert headers["Content-Type"] == "application/x-www-form-urlencoded"
            assert headers["Accept"] == "application/json"

            if data["grant_type"] == "password":
                # check data
                assert data["username"] == "test"
                assert data["password"] == "test123"

                # should use form data instead of json
                assert as_json is False

                # return mock response
                did_get_token = True
                return ClientResponseMock(
                    data={
                        "access_token": "acc-token-1",
                        "refresh_token": "ref-token-1",
                        "token_type": "Bearer",
                        "expires_in": 30,  # ultra short-lived to test token refresh
                    },
                    cookies=[
                        ("JSESSIONID", "session-id"),
                    ],
                )
            elif data["grant_type"] == "refresh_token":
                # token refresh requires session cookie
                assert headers["Cookie"] == "JSESSIONID=session-id"

                # check data
                assert data["refresh_token"] == "ref-token-1"

                # should use form data instead of json
                assert as_json is False

                # return mock response
                did_refresh_token = True
                return ClientResponseMock(
                    data={
                        "access_token": "acc-token-2",
                        "refresh_token": "ref-token-2",
                        "token_type": "Bearer",
                        "expires_in": 3600,  # long-lived
                    },
                    cookies=[
                        ("JSESSIONID", "session-id"),
                    ],
                )

        # DELETE /api/v1/token (logout)
        if method == "DELETE":
            assert endpoint == f"refreshtoken?refreshToken={quote('ref-token-2')}"
            did_delete_token = True

            return ClientResponseMock(data={}, cookies=[])

        raise Exception(f"unexpected endpoint: {endpoint}")

    # create the client
    sma = SMAApiClient(
        host="sma.local",
        username="test",
        password="test123",
        session=mock.MagicMock(),
        use_ssl=False,
    )

    # patch make_request
    with mock.patch.object(sma, "_make_request", wraps=make_request_mock):
        # login should get a new token
        assert (await sma.login()) == LOGIN_RESULT_NEW_TOKEN
        assert did_get_token is True
        assert did_refresh_token is False
        assert did_delete_token is False

        did_get_token = False

        # token is super short-lived, so another login should refresh it
        assert (await sma.login()) == LOGIN_RESULT_TOKEN_REFRESHED
        assert did_get_token is False
        assert did_refresh_token is True
        assert did_delete_token is False

        did_refresh_token = False

        # now the token is long-lived, so another login should do nothing
        assert (await sma.login()) == LOGIN_RESULT_ALREADY_LOGGED_IN
        assert did_get_token is False
        assert did_refresh_token is False
        assert did_delete_token is False

        # logout
        await sma.logout()
        assert did_delete_token is True


@pytest.mark.asyncio
async def test_client_get_all_components():
    """Test SMAApiClient.get_all_components."""

    # mock for make_request
    did_get_root = False
    did_get_children = False
    did_get_inv1_widget = False
    did_get_inv1_extra = False
    did_get_inv2_widget = False
    did_get_inv2_extra = False
    did_get_inv3_widget = False
    did_get_inv3_extra = False
    did_get_inv4_widget = False
    did_get_inv4_extra = False

    async def make_request_mock(
        method: str,
        endpoint: str,
        data: dict | None = None,
        headers: dict | None = None,
        as_json: bool = True,
    ):
        """Mock for make_request."""
        nonlocal did_get_root
        nonlocal did_get_children
        nonlocal did_get_inv1_widget
        nonlocal did_get_inv1_extra
        nonlocal did_get_inv2_widget
        nonlocal did_get_inv2_extra
        nonlocal did_get_inv3_widget
        nonlocal did_get_inv3_extra
        nonlocal did_get_inv4_widget
        nonlocal did_get_inv4_extra

        # required for login
        if method == "POST" and endpoint == "token":
            return ClientResponseMock(
                data={
                    "access_token": "acc-token-1",
                    "refresh_token": "ref-token-1",
                    "token_type": "Bearer",
                    "expires_in": 30,  # ultra short-lived to test token refresh
                },
                cookies=[
                    ("JSESSIONID", "session-id"),
                ],
            )

        # GET /api/v1/navigation (component discovery)
        if method == "GET" and endpoint.startswith("navigation"):
            # check common headers
            assert headers is not None

            # origin headers
            assert headers["Origin"] == "http://sma.local/api/v1"
            assert headers["Host"] == "sma.local"
            # session cookie
            assert headers["Cookie"] == "JSESSIONID=session-id"
            # auth header
            assert headers["Authorization"] == "Bearer acc-token-1"
            # content type headers
            assert headers["Accept"] == "application/json"

            # body is json
            assert as_json is True

            # ROOT component
            if endpoint == "navigation":
                did_get_root = True
                return ClientResponseMock(
                    data=[
                        {
                            "componentId": "plant0",
                            "componentType": "Plant",
                            "name": "The Plant",
                        },
                    ]
                )

            # children of ROOT component
            if endpoint == f"navigation?parentId={quote('plant0')}":
                did_get_children = True
                return ClientResponseMock(
                    data=[
                        {
                            "componentId": "inv1",
                            "componentType": "Inverter",
                            "name": "The 1st Inverter",
                        },
                        {
                            "componentId": "inv2",
                            "componentType": "Inverter",
                            "name": "The 2nd Inverter",
                        },
                        {
                            "componentId": "inv3",
                            "componentType": "Inverter",
                            "name": "The 3rd Inverter",
                        },
                        {
                            "componentId": "inv4",
                            "componentType": "Inverter",
                            "name": "The 4th Inverter",
                        },
                    ]
                )

        # GET /api/v1/widgets/deviceInfo (component extra info)
        if method == "GET" and endpoint.startswith("widgets/deviceinfo"):
            # check common headers
            assert headers is not None

            # origin headers
            assert headers["Origin"] == "http://sma.local/api/v1"
            assert headers["Host"] == "sma.local"
            # session cookie
            assert headers["Cookie"] == "JSESSIONID=session-id"
            # auth header
            assert headers["Authorization"] == "Bearer acc-token-1"
            # content type headers
            assert headers["Accept"] == "application/json"

            # body is json
            assert as_json is True

            # inv1
            if endpoint == "widgets/deviceinfo?deviceId=inv1":
                did_get_inv1_widget = True
                return ClientResponseMock(
                    data={
                        "name": "widget-inv1-name",
                        "serial": "widget-inv1-serial",
                        "deviceInfoFeatures": [
                            {
                                "infoWidgetType": "FirmwareVersion",
                                "value": "widget-inv1-firmware",
                            }
                        ],
                        "productTagId": 1234,
                    }
                )

            # inv2
            if endpoint == "widgets/deviceinfo?deviceId=inv2":
                did_get_inv2_widget = True
                return ClientResponseMock(
                    data={}  # TODO throw
                )

            # inv3
            if endpoint == "widgets/deviceinfo?deviceId=inv3":
                did_get_inv3_widget = True
                return ClientResponseMock(
                    data={
                        "name": "widget-inv3-name",
                        "serial": "widget-inv3-serial",
                        "deviceInfoFeatures": [
                            {
                                "infoWidgetType": "FirmwareVersion",
                                "value": "widget-inv3-firmware",
                            }
                        ],
                        "productTagId": 2345,
                    }
                )

            # inv4
            if endpoint == "widgets/deviceinfo?deviceId=inv4":
                did_get_inv4_widget = True
                return ClientResponseMock(
                    data={}  # TODO throw
                )

        # GET /api/v1/plants/{plantId}/devices/{componentId} (component extra info)
        if method == "GET" and endpoint.startswith("plants/"):
            # check common headers
            assert headers is not None

            # origin headers
            assert headers["Origin"] == "http://sma.local/api/v1"
            assert headers["Host"] == "sma.local"
            # session cookie
            assert headers["Cookie"] == "JSESSIONID=session-id"
            # auth header
            assert headers["Authorization"] == "Bearer acc-token-1"
            # content type headers
            assert headers["Accept"] == "application/json"

            # body is json
            assert as_json is True

            parts = endpoint.split("/")
            plant = parts[1]
            component = parts[3]

            assert plant == "plant0"
            assert component in ["inv1", "inv2", "inv3", "inv4"]

            if component == "inv1":
                did_get_inv1_extra = True
                return ClientResponseMock(
                    data={
                        "product": "extra-inv1-product",
                        "vendor": "extra-inv1-vendor",
                        "serial": "extra-inv1-serial",
                        "firmwareVersion": "extra-inv1-firmware",
                        "ipAddress": "extra-inv1-ip",
                        "generatorPower": 1234,
                        "productTagId": 9876,
                    }
                )
            if component == "inv2":
                did_get_inv2_extra = True
                return ClientResponseMock(
                    data={
                        "product": "extra-inv2-product",
                        "vendor": "extra-inv2-vendor",
                        "serial": "extra-inv2-serial",
                        "firmwareVersion": "extra-inv2-firmware",
                        "ipAddress": "extra-inv2-ip",
                        "generatorPower": 2345,
                        "productTagId": 8765,
                    }
                )
            if component == "inv3":
                did_get_inv3_extra = True
                return ClientResponseMock(
                    data={}  # TODO throw
                )

            if component == "inv4":
                did_get_inv4_extra = True
                return ClientResponseMock(
                    data={}  # TODO throw
                )

        raise Exception(f"unexpected endpoint: {endpoint}")

    # create the client
    sma = SMAApiClient(
        host="sma.local",
        username="test",
        password="test123",
        session=mock.MagicMock(),
        use_ssl=False,
    )

    # patch make_request
    with mock.patch.object(sma, "_make_request", wraps=make_request_mock):
        assert (await sma.login()) == LOGIN_RESULT_NEW_TOKEN

        # get all components
        all_components = await sma.get_all_components()
        assert did_get_root is True
        assert did_get_children is True
        assert did_get_inv1_widget is True
        assert did_get_inv1_extra is True
        assert did_get_inv2_widget is True
        assert did_get_inv2_extra is True
        assert did_get_inv3_widget is True
        assert did_get_inv3_extra is True

        assert len(all_components) == 5

        # Plant
        assert all_components[0].component_id == "plant0"
        assert all_components[0].component_type == "Plant"
        assert all_components[0].name == "The Plant"

        # inv1 has both widget and extra, extra takes precedence
        assert all_components[1].component_id == "inv1"
        assert all_components[1].component_type == "Inverter"
        assert all_components[1].name == "The 1st Inverter"

        assert all_components[1].vendor == "extra-inv1-vendor"
        assert all_components[1].product_name == "extra-inv1-product"
        assert all_components[1].serial_number == "extra-inv1-serial"
        assert all_components[1].firmware_version == "extra-inv1-firmware"
        assert all_components[1].ip_address == "extra-inv1-ip"
        assert all_components[1].generator_power == 1234
        assert all_components[1].product_tag_id == 9876

        # inv2 has only extra, widget throws. extra is used.
        assert all_components[2].component_id == "inv2"
        assert all_components[2].component_type == "Inverter"
        assert all_components[2].name == "The 2nd Inverter"

        assert all_components[2].vendor == "extra-inv2-vendor"
        assert all_components[2].product_name == "extra-inv2-product"
        assert all_components[2].serial_number == "extra-inv2-serial"
        assert all_components[2].firmware_version == "extra-inv2-firmware"
        assert all_components[2].ip_address == "extra-inv2-ip"
        assert all_components[2].generator_power == 2345
        assert all_components[2].product_tag_id == 8765

        # inv3 has only widget, extra throws. widget is used.
        assert all_components[3].component_id == "inv3"
        assert all_components[3].component_type == "Inverter"
        assert all_components[3].name == "The 3rd Inverter"

        assert all_components[3].vendor is None
        assert all_components[3].product_name == "widget-inv3-name"
        assert all_components[3].serial_number == "widget-inv3-serial"
        assert all_components[3].firmware_version == "widget-inv3-firmware"
        assert all_components[3].ip_address is None
        assert all_components[3].generator_power is None
        assert all_components[3].product_tag_id == 2345

        # inv4 has neither widget nor extra. all extra fields are None.
        assert all_components[4].component_id == "inv4"
        assert all_components[4].component_type == "Inverter"
        assert all_components[4].name == "The 4th Inverter"

        assert all_components[4].vendor is None
        assert all_components[4].product_name is None
        assert all_components[4].serial_number is None
        assert all_components[4].firmware_version is None
        assert all_components[4].ip_address is None
        assert all_components[4].generator_power is None
        assert all_components[4].product_tag_id is None


@pytest.mark.asyncio
async def test_client_get_all_live_measurements():
    """Test SMAApiClient.get_all_live_measurements."""

    # mock for make_request
    did_get_measurements = False

    async def make_request_mock(
        method: str,
        endpoint: str,
        data: dict | None = None,
        headers: dict | None = None,
        as_json: bool = True,
    ):
        """Mock for make_request."""
        nonlocal did_get_measurements

        # required for login
        if method == "POST" and endpoint == "token":
            return ClientResponseMock(
                data={
                    "access_token": "acc-token-1",
                    "refresh_token": "ref-token-1",
                    "token_type": "Bearer",
                    "expires_in": 30,  # ultra short-lived to test token refresh
                },
                cookies=[
                    ("JSESSIONID", "session-id"),
                ],
            )

        # POST /api/v1/measurements/live
        if method == "POST" and endpoint == "measurements/live":
            # check common headers
            assert headers is not None

            # origin headers
            assert headers["Origin"] == "http://sma.local/api/v1"
            assert headers["Host"] == "sma.local"
            # session cookie
            assert headers["Cookie"] == "JSESSIONID=session-id"
            # auth header
            assert headers["Authorization"] == "Bearer acc-token-1"
            # content type headers
            assert headers["Content-Type"] == "application/json"
            assert headers["Accept"] == "application/json"

            # body is json
            assert as_json is True

            # check payload
            assert data is not None
            assert data == [
                {
                    "componentId": "inv0",
                },
                {
                    "componentId": "inv1",
                },
            ]

            # return mock response
            did_get_measurements = True
            return ClientResponseMock(
                data=[
                    {
                        "channelId": "chastt",
                        "componentId": "inv0",
                        "values": [{"time": "2024-02-01T11:30:00Z", "value": 10}],
                    },
                    {
                        "channelId": "chastt",
                        "componentId": "inv1",
                        "values": [{"time": "2024-02-01T11:30:00Z", "value": 25}],
                    },
                ]
            )

        raise Exception(f"unexpected endpoint: {endpoint}")

    # create the client
    sma = SMAApiClient(
        host="sma.local",
        username="test",
        password="test123",
        session=mock.MagicMock(),
        use_ssl=False,
    )

    # patch make_request
    with mock.patch.object(sma, "_make_request", wraps=make_request_mock):
        assert (await sma.login()) == LOGIN_RESULT_NEW_TOKEN

        # get all live measurements
        measurements = await sma.get_all_live_measurements(
            component_ids=["inv0", "inv1"]
        )
        assert did_get_measurements is True

        assert len(measurements) == 2

        # inv0
        assert measurements[0].component_id == "inv0"
        assert measurements[0].channel_id == "chastt"
        assert measurements[0].values[0].time == "2024-02-01T11:30:00Z"
        assert measurements[0].values[0].value == 10

        # inv1
        assert measurements[1].component_id == "inv1"
        assert measurements[1].channel_id == "chastt"
        assert measurements[1].values[0].time == "2024-02-01T11:30:00Z"
        assert measurements[1].values[0].value == 25


@pytest.mark.asyncio
async def test_client_get_live_measurements():
    """Test SMAApiClient.get_live_measurements for regular (non-array) channels."""

    # mock for make_request
    did_get_measurement = False

    async def make_request_mock(
        method: str,
        endpoint: str,
        data: Any | None = None,
        headers: dict | None = None,
        as_json: bool = True,
    ):
        """Mock for make_request."""
        nonlocal did_get_measurement

        # required for login
        if method == "POST" and endpoint == "token":
            return ClientResponseMock(
                data={
                    "access_token": "acc-token-1",
                    "refresh_token": "ref-token-1",
                    "token_type": "Bearer",
                    "expires_in": 30,  # ultra short-lived to test token refresh
                },
                cookies=[
                    ("JSESSIONID", "session-id"),
                ],
            )

        # POST /api/v1/measurements/live
        if method == "POST" and endpoint == "measurements/live":
            # check common headers
            assert headers is not None

            # origin headers
            assert headers["Origin"] == "http://sma.local/api/v1"
            assert headers["Host"] == "sma.local"
            # session cookie
            assert headers["Cookie"] == "JSESSIONID=session-id"
            # auth header
            assert headers["Authorization"] == "Bearer acc-token-1"
            # content type headers
            assert headers["Content-Type"] == "application/json"
            assert headers["Accept"] == "application/json"

            # body is json
            assert as_json is True

            # check payload
            assert data is not None
            assert data == [
                {
                    "componentId": "inv0",
                    "channelId": "chastt",
                },
            ]

            # return mock response
            did_get_measurement = True
            return ClientResponseMock(
                data=[
                    {
                        "channelId": "chastt",
                        "componentId": "inv0",
                        "values": [{"time": "2024-02-01T11:30:00Z", "value": 10}],
                    },
                ]
            )

        raise Exception(f"unexpected endpoint: {endpoint}")

    # create the client
    sma = SMAApiClient(
        host="sma.local",
        username="test",
        password="test123",
        session=mock.MagicMock(),
        use_ssl=False,
    )

    # patch make_request
    with mock.patch.object(sma, "_make_request", wraps=make_request_mock):
        assert (await sma.login()) == LOGIN_RESULT_NEW_TOKEN

        # get live measurement
        measurements = await sma.get_live_measurements(
            [
                LiveMeasurementQueryItem(
                    component_id="inv0",
                    channel_id="chastt",
                )
            ]
        )
        assert did_get_measurement is True

        assert len(measurements) == 1

        # inv0
        assert measurements[0].component_id == "inv0"
        assert measurements[0].channel_id == "chastt"
        assert measurements[0].values[0].time == "2024-02-01T11:30:00Z"
        assert measurements[0].values[0].value == 10


@pytest.mark.asyncio
async def test_client_get_live_measurements_array():
    """Test SMAApiClient.get_live_measurements with array channels.

    array channels are channels that contain multiple values in a single measurement.
    they are used by, among others, the "Measurement.DcMs.Vol[]" channels (see https://github.com/shadow578/homeassistant_sma_data_manager/issues/20).

    the client treats array channels as multiple channels with the index added to the channel id.
    """

    # mock for make_request
    did_get_measurement = False

    async def make_request_mock(
        method: str,
        endpoint: str,
        data: dict | None = None,
        headers: dict | None = None,
        as_json: bool = True,
    ):
        """Mock for make_request."""
        nonlocal did_get_measurement

        # required for login
        if method == "POST" and endpoint == "token":
            return ClientResponseMock(
                data={
                    "access_token": "acc-token-1",
                    "refresh_token": "ref-token-1",
                    "token_type": "Bearer",
                    "expires_in": 30,  # ultra short-lived to test token refresh
                },
                cookies=[
                    ("JSESSIONID", "session-id"),
                ],
            )

        # POST /api/v1/measurements/live
        if method == "POST" and endpoint == "measurements/live":
            # check common headers
            assert headers is not None

            # origin headers
            assert headers["Origin"] == "http://sma.local/api/v1"
            assert headers["Host"] == "sma.local"
            # session cookie
            assert headers["Cookie"] == "JSESSIONID=session-id"
            # auth header
            assert headers["Authorization"] == "Bearer acc-token-1"
            # content type headers
            assert headers["Content-Type"] == "application/json"
            assert headers["Accept"] == "application/json"

            # body is json
            assert as_json is True

            # check payload
            assert data is not None
            assert data == [
                {
                    "componentId": "inv0",
                    "channelId": "arrtst[]",
                },
            ]

            # return mock response
            did_get_measurement = True
            return ClientResponseMock(
                data=[
                    {
                        "channelId": "arrtst[]",
                        "componentId": "inv0",
                        "values": [
                            {
                                "time": "2024-02-01T11:30:00Z",
                                "values": [
                                    10,  # arrtst[0]
                                    20,  # arrtst[1]
                                ],
                            }
                        ],
                    },
                ]
            )

        raise Exception(f"unexpected endpoint: {endpoint}")

    # create the client
    sma = SMAApiClient(
        host="sma.local",
        username="test",
        password="test123",
        session=mock.MagicMock(),
        use_ssl=False,
    )

    # patch make_request
    with mock.patch.object(sma, "_make_request", wraps=make_request_mock):
        assert (await sma.login()) == LOGIN_RESULT_NEW_TOKEN

        # get live measurement
        measurements = await sma.get_live_measurements(
            [
                LiveMeasurementQueryItem(
                    component_id="inv0",
                    channel_id="arrtst[]",
                )
            ]
        )
        assert did_get_measurement is True

        assert len(measurements) == 2

        # inv0 - arrtst entry 0
        assert measurements[0].component_id == "inv0"
        assert measurements[0].channel_id == "arrtst[0]"
        assert measurements[0].values[0].time == "2024-02-01T11:30:00Z"
        assert measurements[0].values[0].value == 10

        # inv0 - arrtst entry 1
        assert measurements[1].component_id == "inv0"
        assert measurements[1].channel_id == "arrtst[1]"
        assert measurements[1].values[0].time == "2024-02-01T11:30:00Z"
        assert measurements[1].values[0].value == 20
