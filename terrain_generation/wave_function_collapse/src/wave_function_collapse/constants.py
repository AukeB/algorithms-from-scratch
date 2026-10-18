"""Module for project constants and shared type definitions."""

from pathlib import Path
from typing import NamedTuple

_PACKAGE_DIRECTORY = Path(__file__).parent

CONFIG_FILE_PATH = _PACKAGE_DIRECTORY / "configs" / "config.yaml"
BITMAPS_INPUT_DIRECTORY_PATH = _PACKAGE_DIRECTORY / "bitmaps" / "input"
BITMAPS_EXPORT_DIRECTORY_PATH = _PACKAGE_DIRECTORY / "bitmaps" / "export"

# Ratio between the PyGame window size and the desktop resolution.
WINDOW_SIZE_SCREEN_FRACTION = 0.95

type RGBColor = tuple[int, int, int]
type TileValue = tuple[tuple[str, ...], ...]

# Offsets (row, column) from a grid cell to its neighbor in each direction.
DIRECTIONS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


class Dimensions(NamedTuple):
    """Count of elements in rows and columns.

    Attributes:
        rows (int): Number of rows.
        cols (int): Number of columns.
    """

    rows: int
    cols: int


class Size(NamedTuple):
    """Pixel extent of an object.

    Attributes:
        width (int): Width in pixels.
        height (int): Height in pixels.
    """

    width: int
    height: int
