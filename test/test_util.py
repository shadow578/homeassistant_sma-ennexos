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


def test_channel_parts_to_entity_id_umlauts():
    """
    Test entity ids are created as expected when umlauts and other special characters are involved.

    SMA device names support umlauts (in fact, german installations [by lazy electricians] default their name to "Mein Gerät"),
    but homeassistant entity ids only support ascii characters (a-z, 0-9, and underscores).
    until now, homeassistant would automatically fix the ids for us, but starting in 2027.2.0, this is deprecated.
    """
    assert (
        channel_parts_to_entity_id("Mein Gerät", "Measurement.GridMs.Hz", "sensor")
        == "sensor.mein_geraet_measurement_gridms_hz"
    )
    assert (
        channel_parts_to_entity_id("Test äöüß!", "ch.äöüß", "sensor")
        == "sensor.test_aeoeuess_ch_aeoeuess"
    )

    # eastern arabic numerals and other weirdness should be dropped
    assert (
        channel_parts_to_entity_id("Test ١٨زب", "ch.a", "sensor") == "sensor.test_ch_a"
    )

    # if you do this, i hate you
    assert channel_parts_to_entity_id("Test ☀️☀️", "test", "sensor") == "sensor.test_test"


def test_channel_parts_to_entity_id_umlauts_old():
    """
    Test entity ids are created as expected when umlauts and other special characters are involved, using the old normalization method.

    This is to verify that, with the update, existing sensors are not broken.
    """
    assert (
        channel_parts_to_entity_id(
            "Mein Gerät", "Measurement.GridMs.Hz", "sensor", normalization="old"
        )
        == "sensor.mein_gerät_measurement_gridms_hz"
    )
    assert (
        channel_parts_to_entity_id(
            "Test äöüß!", "ch.äöüß", "sensor", normalization="old"
        )
        == "sensor.test_äöüß_ch_äöüß"
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
