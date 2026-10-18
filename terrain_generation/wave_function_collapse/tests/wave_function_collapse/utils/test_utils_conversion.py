"""Tests for the utils_conversion module."""

from wave_function_collapse.utils.utils_conversion import hex_to_rgb


# Testing the "hex_to_rgb" function.


def test_hex_to_rgb_splits_the_components() -> None:
    assert hex_to_rgb(color_hex="FF8800") == (255, 136, 0)


def test_hex_to_rgb_accepts_lowercase() -> None:
    assert hex_to_rgb(color_hex="0a0b0c") == (10, 11, 12)
