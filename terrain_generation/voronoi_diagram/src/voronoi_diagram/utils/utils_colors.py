"""Module for generating the colors of the Voronoi regions and seed points."""

import colorsys

from voronoi_diagram.constants import RGBColor

_HUE_RANGE = 0.75  # Stops before the purple hues, which blend into the background.
_SATURATION = 0.5
_BRIGHT_VALUE = 0.95
_DARK_FACTOR = 0.6  # Seed points are drawn darker than the cells around them.


def _hsv_to_rgb_color(hue: float, saturation: float, value: float) -> RGBColor:
    """Convert an HSV color with components in [0, 1] to an 8-bit RGB color.

    Args:
        hue (float): Hue in [0, 1].
        saturation (float): Saturation in [0, 1].
        value (float): Brightness in [0, 1].

    Returns:
        rgb_color (RGBColor): The color as 8-bit RGB values.
    """
    red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
    rgb_color: RGBColor = (int(red * 255), int(green * 255), int(blue * 255))

    return rgb_color


def generate_voronoi_colors(
    num_seeds: int,
) -> tuple[list[RGBColor], list[RGBColor]]:
    """Generate the seed point and cell colors, with hues spread evenly around the wheel.

    Args:
        num_seeds (int): Number of colors to generate for each palette.

    Returns:
        colors (tuple[list[RGBColor], list[RGBColor]]): The seed point colors (darker) and the
            voronoi cell colors (bright), one of each per seed.
    """
    seed_colors: list[RGBColor] = []
    cell_colors: list[RGBColor] = []

    for index in range(num_seeds):
        hue = (index / num_seeds) * _HUE_RANGE

        seed_color = _hsv_to_rgb_color(hue, _SATURATION, _BRIGHT_VALUE * _DARK_FACTOR)
        seed_colors.append(seed_color)

        cell_color = _hsv_to_rgb_color(hue, _SATURATION, _BRIGHT_VALUE)
        cell_colors.append(cell_color)

    colors = (seed_colors, cell_colors)

    return colors
