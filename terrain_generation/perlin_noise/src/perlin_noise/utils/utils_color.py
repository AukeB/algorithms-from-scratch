"""Utility module with functions related to colors."""

from src.perlin_noise.constants import RGBColor


def lerp_color(color_value: RGBColor, noise_value: float) -> RGBColor:
    """Linearly interpolate from a base color to a target color.

    The interpolation uses a fixed base color (white) and blends it
    toward the provided target color based on a noise-derived scalar.

    Args:
        color_value (tuple): RGB target color.
        noise_value (float): Normalized scalar in range [0, 1]
            representing intensity (e.g., noise or normalized value).

    Returns:
        tuple: Interpolated RGB color.
    """
    base = (255, 255, 255)
    interpolated_color_value: RGBColor = tuple(
        int(base[i] + (color_value[i] - base[i]) * noise_value) for i in range(3)
    )  # type: ignore

    return interpolated_color_value
