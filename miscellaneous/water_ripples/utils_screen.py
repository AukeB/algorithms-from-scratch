"""Pygame helpers for picking a window size from the desktop resolution."""

import pygame as pg

from constants import WINDOW_SIZE_SCREEN_FRACTION


def window_size_from_screen() -> tuple[int, int]:
    """
    Windowed (non-fullscreen) size: a fraction of the primary desktop resolution.

    Uses pygame.display.get_desktop_sizes() when available, otherwise
    pygame.display.Info().
    """
    if not pg.get_init():
        pg.init()
    get_sizes = getattr(pg.display, "get_desktop_sizes", None)
    sizes = get_sizes() if get_sizes is not None else []
    if sizes:
        desktop_w, desktop_h = sizes[0]
    else:
        info = pg.display.Info()
        desktop_w = info.current_w or 1920
        desktop_h = info.current_h or 1080
    frac = WINDOW_SIZE_SCREEN_FRACTION
    w = max(1, int(desktop_w * frac))
    h = max(1, int(desktop_h * frac))
    return w, h


def resolve_window_and_grid(
    window_width: int | None,
    window_height: int | None,
    number_of_columns: int,
    number_of_rows: int | None,
) -> tuple[int, int, int]:
    """
    Resolve window size and row count for the simulation grid.

    If both window_width and window_height are None, uses window_size_from_screen(). If both are
    set, uses those values. If only one is set, raises ValueError.

    If number_of_rows is None, sets it from the window aspect ratio and
    number_of_columns.
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
