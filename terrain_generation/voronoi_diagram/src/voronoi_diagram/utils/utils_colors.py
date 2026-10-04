"""Module for utility functions related to clors.."""

import colorsys


def generate_voronoi_colors(
    num_seeds: int,
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]]:
    """Generates bright and darkened color palettes for seed points and cells.

    Distributes hues evenly across the color wheel while keeping saturation and
    value constant. Returns both bright colors (for cells) and darkened versions
    (for seed points).

    Args:
        num_seeds (int): Number of colors to generate.

    Returns:
        colors (tuple): (seed_point_colors, voronoi_cell_colors), each a list of
            RGB color tuples.
    """
    seed_colors = []
    cell_colors = []

    for i in range(num_seeds):
        hue = (i / num_seeds) * 0.75  # Skip purple range
        saturation = 0.5
        value = 0.95

        # Darkened color for seed point
        darkened_value = value * 0.6
        rgb_dark = colorsys.hsv_to_rgb(hue, saturation, darkened_value)
        seed_colors.append(tuple(int(c * 255) for c in rgb_dark))

        # Bright color for cell
        rgb_bright = colorsys.hsv_to_rgb(hue, saturation, value)
        cell_colors.append(tuple(int(c * 255) for c in rgb_bright))

    return seed_colors, cell_colors
