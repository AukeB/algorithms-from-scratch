"""Module for storing project constants."""

from pathlib import Path
from typing import NamedTuple

# Project directory and file paths.
CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.yaml"

# PyGame setup.
WINDOW_SIZE_SCREEN_FRACTION: float = 0.9


class Dimensions(NamedTuple):
    """Structural properties of a grid, matrix, or layout.

    The number of columns and rows into which the grid is partitioned.

    Attributes:
        rows (int): Number of rows.
        cols (int): Number of columns.
    """

    rows: int
    cols: int


class Size(NamedTuple):
    """Spatial extent of an object.

    Expressed in pixels, but any unit of physical distance may be employed.

    Attributes:
        width (int): Width of the object.
        height (int): Height of the object.
    """

    width: int
    height: int


class Position(NamedTuple):
    """Location using `x` and `y` coordinates.

    May be a position on the screen in pixel units, or a location within a grid
    or board, expressed in terms of columns and rows.

    Attributes:
        x (int): Horizontal coordinate.
        y (int): Vertical coordinate.
    """

    x: int
    y: int
