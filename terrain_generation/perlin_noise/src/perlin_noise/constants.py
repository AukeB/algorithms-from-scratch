"""Module for project constants and shared type definitions."""

from pathlib import Path
from typing import Literal, NamedTuple

CONFIG_FILE_PATH = Path(__file__).parent / "configs" / "config.yaml"

# Ratio between the PyGame window size and the desktop resolution.
WINDOW_SIZE_SCREEN_FRACTION = 0.95

type RGBColor = tuple[int, int, int]
type SmoothingVersion = Literal["original", "revised"]


class Dimensions(NamedTuple):
    """Structural size of a grid, in rows and columns.

    Attributes:
        rows (int): Number of rows.
        cols (int): Number of columns.
    """

    rows: int
    cols: int


class Size(NamedTuple):
    """Physical extent of an object, in width and height.

    Attributes:
        width (int): Width in pixels.
        height (int): Height in pixels.
    """

    width: int
    height: int
