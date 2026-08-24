# Module for storing project constants.

from collections import namedtuple
from pathlib import Path

# Project directory and file paths.
CONFIG_PATH = Path("src/eca/configs/config.yaml")

# PyGame setup.
WINDOW_SIZE_SCREEN_FRACTION: float = 0.9

"""
- `Dimensions` refers to the structural properties of a grid, matrix, or layout,
  specifying the number of columns and rows into which the grid is partitioned.
- `Size` denotes the physical or spatial extent of an object, characterized by
  its width and height. These measurements are typically expressed in pixels,
  but any unit of physical distance may be employed.
- `Position` specifies a location using `x` and `y` coordinates. These
  coordinates may represent a position on the screen in pixel units, or a
  location within a grid or board, expressed in terms of columns and rows.
"""
Dimensions = namedtuple("Dimensions", "rows cols")
Size = namedtuple("Size", "width height")
Position = namedtuple("Position", "x y")
