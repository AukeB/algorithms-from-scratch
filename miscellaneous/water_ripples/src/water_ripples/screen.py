"""Module for picking the window size and the simulation grid from the desktop resolution."""

import pygame as pg

from water_ripples.constants import WINDOW_SIZE_SCREEN_FRACTION


def window_size_from_screen(
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


def resolve_window_and_grid(
    window_width: int | None,
    window_height: int | None,
    number_of_columns: int,
    number_of_rows: int | None,
) -> tuple[int, int, int]:
    """Resolve the window size and the number of rows of the simulation grid.

    Args:
        window_width (int | None): Window width in pixels, or None for automatic sizing.
        window_height (int | None): Window height in pixels, or None for automatic sizing.
        number_of_columns (int): Number of columns in the simulation grid.
        number_of_rows (int | None): Number of rows, or None to match the window aspect ratio.

    Returns:
        resolved (tuple[int, int, int]): The window width, window height and number of rows.

    Raises:
        ValueError: If exactly one of window_width or window_height is None.
    """
    if window_width is None and window_height is None:
        window_width, window_height = window_size_from_screen()
    elif window_width is None or window_height is None:
        raise ValueError(
            "window_width and window_height must both be None for automatic sizing, "
            "or both be integers"
        )

    if number_of_rows is None:
        number_of_rows = int(number_of_columns * window_height / window_width)

    resolved = (window_width, window_height, number_of_rows)

    return resolved
