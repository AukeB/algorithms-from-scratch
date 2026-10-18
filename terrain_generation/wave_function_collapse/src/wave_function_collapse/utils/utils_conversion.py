"""Module for converting between colour representations."""

from wave_function_collapse.constants import RGBColor


def hex_to_rgb(color_hex: str) -> RGBColor:
    """Convert a 6-character hex colour string to an RGB tuple.

    Args:
        color_hex (str): A 6-character hexadecimal colour string, such as "FF8800".

    Returns:
        rgb_color (RGBColor): The red, green and blue components.
    """
    red = int(color_hex[0:2], 16)
    green = int(color_hex[2:4], 16)
    blue = int(color_hex[4:6], 16)
    rgb_color: RGBColor = (red, green, blue)

    return rgb_color
