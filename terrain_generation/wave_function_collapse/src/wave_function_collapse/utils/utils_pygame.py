"""Module for pygame display helpers."""

import pygame as pg

from wave_function_collapse.constants import WINDOW_SIZE_SCREEN_FRACTION


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
