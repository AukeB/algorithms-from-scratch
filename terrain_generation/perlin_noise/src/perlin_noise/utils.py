"""Utility module with helper functions."""

import pygame as pg

from src.perlin_noise.constants import WINDOW_SIZE_SCREEN_FRACTION, RGBColor


def get_window_size_from_screen_resolution(
    monitor_index: int = 0,
    min_width: int = 400,
    min_height: int = 300,
) -> tuple[int, int]:
    """
    Compute a windowed (non-fullscreen) size as a fraction of the primary desktop resolution.

    1. Initialise the pygame display module if not already active.
    2. Attempt to read the desktop resolution via get_desktop_sizes() (pygame >= 2.0).
    3. Fall back to display.Info() for older pygame versions.
    4. Apply WINDOW_SIZE_SCREEN_FRACTION and clamp to the minimum dimensions.

    Args:
        monitor_index (int): Index of the monitor to use from get_desktop_sizes().
        min_width (int): Minimum window width in pixels.
        min_height (int): Minimum window height in pixels.

    Returns:
        tuple[int, int]: The window width and height in pixels.
    """
    # Init
    if not pg.display.get_init():
        pg.display.init()

    # Resolve desktop resolution
    if pg.version.vernum >= (2, 0, 0):
        desktop_width, desktop_height = pg.display.get_desktop_sizes()[monitor_index]
    else:
        info = pg.display.Info()
        desktop_width = info.current_w if info.current_w > 0 else 1920
        desktop_height = info.current_h if info.current_h > 0 else 1080

    # Scale
    width = max(min_width, int(desktop_width * WINDOW_SIZE_SCREEN_FRACTION))
    height = max(min_height, int(desktop_height * WINDOW_SIZE_SCREEN_FRACTION))

    return width, height


def lerp_color(color_value: RGBColor, noise_value: float) -> RGBColor:
    """
    Linearly interpolate from a base color to a target color.

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


def smooth_perline_polyominal(t: float, smoothing_version: str) -> float:  # type: ignore
    """
    Compute Perlin smoothing for a given value.

    Args:
        t (float): Input value in the range [0, 1].
        smoothing_version (str): Smoothing type. Use "original" for the classic
            polynomial or "revised" for the 2002 improved version.

    Returns:
        float: Smoothed value.

    Raises:
        ValueError: If an unknown version is provided.
    """
    if smoothing_version == "original":
        return t * t * (3.0 - 2.0 * t)
    elif smoothing_version == "revised":
        return t**3 * (t * (t * 6.0 - 15.0) + 10.0)
