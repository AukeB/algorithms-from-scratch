"""Module for helper functions: window sizing, color blending and smoothing."""

import pygame as pg

from perlin_noise.constants import (
    WINDOW_SIZE_SCREEN_FRACTION,
    RGBColor,
    SmoothingVersion,
)

_WHITE: RGBColor = (255, 255, 255)


def get_window_size_from_screen_resolution(
    monitor_index: int = 0,
    min_width: int = 400,
    min_height: int = 300,
) -> tuple[int, int]:
    """Compute a windowed (non-fullscreen) size as a fraction of the desktop resolution.

    Args:
        monitor_index (int): Index of the monitor to use from get_desktop_sizes().
        min_width (int): Minimum window width in pixels.
        min_height (int): Minimum window height in pixels.

    Returns:
        window_size (tuple[int, int]): The window width and height in pixels.
    """
    if not pg.display.get_init():
        pg.display.init()

    desktop_sizes = pg.display.get_desktop_sizes()
    desktop_size = desktop_sizes[monitor_index]
    desktop_width, desktop_height = desktop_size

    scaled_width = int(desktop_width * WINDOW_SIZE_SCREEN_FRACTION)
    scaled_height = int(desktop_height * WINDOW_SIZE_SCREEN_FRACTION)

    width = max(min_width, scaled_width)
    height = max(min_height, scaled_height)
    window_size = (width, height)

    return window_size


def _blend_channel(base: int, target: int, weight: float) -> int:
    """Blend one color channel from a base value toward a target value.

    Args:
        base (int): Channel value at weight 0.
        target (int): Channel value at weight 1.
        weight (float): Blend weight in [0, 1].

    Returns:
        blended (int): The blended channel value.
    """
    blended = int(base + (target - base) * weight)

    return blended


def lerp_color(color_value: RGBColor, noise_value: float) -> RGBColor:
    """Linearly interpolate from white toward a target color.

    Args:
        color_value (RGBColor): The target color, reached at noise_value 1.
        noise_value (float): Blend weight in [0, 1].

    Returns:
        interpolated_color_value (RGBColor): The blended color.
    """
    red = _blend_channel(_WHITE[0], color_value[0], noise_value)
    green = _blend_channel(_WHITE[1], color_value[1], noise_value)
    blue = _blend_channel(_WHITE[2], color_value[2], noise_value)
    interpolated_color_value: RGBColor = (red, green, blue)

    return interpolated_color_value


def smooth_perlin_polynomial(t: float, smoothing_version: SmoothingVersion) -> float:
    """Apply the Perlin fade curve to a value in [0, 1].

    Args:
        t (float): Input value in the range [0, 1].
        smoothing_version (SmoothingVersion): "original" for the classic cubic curve, or
            "revised" for the quintic curve from 2002.

    Returns:
        smoothed (float): The smoothed value.
    """
    if smoothing_version == "original":
        smoothed = t * t * (3.0 - 2.0 * t)
    else:
        smoothed = t**3 * (t * (t * 6.0 - 15.0) + 10.0)

    return smoothed
