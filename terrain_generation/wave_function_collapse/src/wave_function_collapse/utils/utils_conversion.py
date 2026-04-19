"""Utility module with functions related to conversion."""

from src.wave_function_collapse.constants import RGBColor


def hex_to_rgb(color_hex: str) -> RGBColor:
    """
    Convert a 6-character hex color string to an RGB tuple.

    1. Extract the red, green, and blue components from the hex string.
    2. Convert each component from base-16 to an integer.
    3. Return the three components as a tuple.

    Args:
        color_hex (str): A 6-character hexadecimal color string, e.g. 'FF8800'.

    Returns:
        rgb_tuple (tuple[int, int, int]): A tuple of (red, green, blue) integer values.
    """
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)

    rgb_tuple = (r, g, b)

    return rgb_tuple
