"""Sanity checks for the test suite."""

from unittest import mock

import pytest

from custom_components.sma_ennexos.sma.client import (
    LOGIN_RESULT_ALREADY_LOGGED_IN,
    SMAApiClient,
)
from custom_components.sma_ennexos.sma.model import (
    ChannelValues,
    ComponentInfo,
    LiveMeasurementQueryItem,
    TimeValuePair,
)


@pytest.mark.asyncio
async def test_sma_client_mock_fixture_counters_and_data(mock_sma_client):
    """Quick sanity-check the mock_sma_client fixture works as expected."""

    sma = SMAApiClient(
        host="sma.local",
        username="user",
        password="password",
        session=mock.MagicMock(),
        use_ssl=False,
    )

    mock_sma_client.reset_counts()
    assert mock_sma_client.cnt_login == 0
    assert await sma.login() == LOGIN_RESULT_ALREADY_LOGGED_IN
    assert mock_sma_client.cnt_login == 1

    mock_sma_client.reset_counts()
    assert mock_sma_client.cnt_logout == 0
    await sma.logout()
    assert mock_sma_client.cnt_logout == 1

    mock_sma_client.reset_counts()
    mock_sma_client.components = [
        ComponentInfo(
            component_id="component1",
            component_type="type1",
            name="name1",
        )
    ]

    assert mock_sma_client.cnt_get_all_components == 0
    components = await sma.get_all_components()
    assert mock_sma_client.cnt_get_all_components == 1

    assert len(components) == 1
    assert components[0].component_id == "component1"

    mock_sma_client.reset_counts()
    mock_sma_client.measurements = [
        ChannelValues(
            channel_id="channel1",
            component_id="component1",
            values=[
                TimeValuePair(
                    time="2021-01-01T00:00:00Z",
                    value=1.0,
                )
            ],
        )
    ]

    assert mock_sma_client.cnt_get_all_live_measurements == 0
    measurements = await sma.get_all_live_measurements(
        component_ids=["component1"],
    )
    assert mock_sma_client.cnt_get_all_live_measurements == 1

    assert len(measurements) == 1
    assert measurements[0].channel_id == "channel1"

    mock_sma_client.reset_counts()
    assert mock_sma_client.cnt_get_live_measurements == 0
    measurements = await sma.get_live_measurements(
        query=[
            LiveMeasurementQueryItem(
                component_id="component1",
                channel_id="channel1",
            )
        ]
    )
    assert mock_sma_client.cnt_get_live_measurements == 1

    assert len(measurements) == 1
    assert measurements[0].channel_id == "channel1"


@pytest.mark.asyncio
async def test_sma_client_mock_fixture_hooks(mock_sma_client):
    """Quick sanity-check the mock_sma_client fixture works as expected."""

    sma = SMAApiClient(
        host="sma.local",
        username="user",
        password="password",
        session=mock.MagicMock(),
        use_ssl=False,
    )

    # errors raised in hook function should be propagated
    def on_login():
        raise ValueError("testing hook error")

    mock_sma_client.on_login = on_login

    with pytest.raises(ValueError):
        await sma.login()
