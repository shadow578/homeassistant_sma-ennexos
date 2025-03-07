"""Test the utility functions."""

from custom_components.sma_ennexos.util import (
    channel_parts_to_entity_id,
    channel_to_translation_key,
)


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


def test_channel_id_to_translation_key():
    """Test channel_ids are converted to translation keys as expected."""
    assert (
        channel_to_translation_key("Measurement.Metering.GridMs.TotWIn.Bat")
        == "measurement_metering_gridms_totwin_bat"
    )

    # array channel drops index
    assert (
        channel_to_translation_key("Measurement.DcMs.Watt[0]")
        == "measurement_dcms_watt"
    )
    assert (
        channel_to_translation_key("Measurement.DcMs.Watt[1]")
        == "measurement_dcms_watt"
    )
