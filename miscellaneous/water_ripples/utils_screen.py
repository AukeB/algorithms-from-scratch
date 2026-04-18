"""Pygame helpers for picking a window size from the desktop resolution."""

import numpy as np
import pygame as pg
from constants import WINDOW_SIZE_SCREEN_FRACTION


def window_size_from_screen(
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


def resolve_window_and_grid(
    window_width: int | None,
    window_height: int | None,
    number_of_columns: int,
    number_of_rows: int | None,
) -> tuple[int, int, int]:
    """
    Resolve window size and row count for the simulation grid.

    If both window_width and window_height are None, uses window_size_from_screen().
    If both are set, uses those values. If only one is set, raises ValueError.
    If number_of_rows is None, sets it from the window aspect ratio and
    number_of_columns.

    Args:
        window_width (int | None): The desired window width in pixels, or None
            for automatic sizing.
        window_height (int | None): The desired window height in pixels, or None
            for automatic sizing.
        number_of_columns (int): The number of columns in the simulation grid.
        number_of_rows (int | None): The number of rows in the simulation grid,
            or None to derive it from the window aspect ratio.

    Returns:
        tuple[int, int, int]: The resolved window width, window height, and
            number of rows.

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

    return window_width, window_height, number_of_rows


def resize_bool_mask_nearest(mask: np.ndarray, out_h: int, out_w: int) -> np.ndarray:
    """
    Scale a 2D boolean mask to (out_h, out_w) with nearest-neighbor sampling.

    Args:
        mask (np.ndarray): A 2D boolean array to resize.
        out_h (int): The desired output height in pixels.
        out_w (int): The desired output width in pixels.

    Returns:
        np.ndarray: A 2D boolean array of shape (out_h, out_w).
    """
    in_h, in_w = int(mask.shape[0]), int(mask.shape[1])

    y_src = np.floor(np.arange(out_h, dtype=np.float64) * in_h / out_h).astype(np.intp)
    x_src = np.floor(np.arange(out_w, dtype=np.float64) * in_w / out_w).astype(np.intp)

    y_src = np.clip(y_src, 0, in_h - 1)
    x_src = np.clip(x_src, 0, in_w - 1)

    return mask[y_src[:, None], x_src[None, :]]
