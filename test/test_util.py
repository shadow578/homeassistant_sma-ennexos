"""Test the utility functions."""

from custom_components.sma_ennexos.util import (
    channel_fqid_to_parts,
    channel_parts_to_entity_id,
    channel_parts_to_fqid,
)


def test_channel_parts_to_fqid():
    """Test channel FQID creation works."""
    assert channel_parts_to_fqid("component1", "channel1") == "channel1@component1"


def test_channel_fqid_to_parts():
    """Test channel FQID parsing works."""
    assert channel_fqid_to_parts("channel1@component1") == ("component1", "channel1")


def test_channel_parts_to_entity_id():
    """Test entity ids are created as expected."""
    assert (
        channel_parts_to_entity_id("component1", "channel1", "sensor")
        == "sensor.component1_channel1"
    )
    assert (
        channel_parts_to_entity_id(
            "My Plant", "Measurement.Metering.GridMs.TotWIn.Bat", "sensor"
        )
        == "sensor.my_plant_measurement_metering_gridms_totwin_bat"
    )

    # array channels end in _0, _1, _2, etc.
    assert (
        channel_parts_to_entity_id("My Plant", "Measurement.DcMs.Watt[0]", "sensor")
        == "sensor.my_plant_measurement_dcms_watt_0"
    )
    assert (
        channel_parts_to_entity_id("My Plant", "Measurement.DcMs.Watt[1]", "sensor")
        == "sensor.my_plant_measurement_dcms_watt_1"
    )
