"""Project-specific constants."""

from collections import namedtuple
from pathlib import Path

# Paths.
CONFIG_FILE_PATH = Path("src/perlin_noise/configs/config.yaml")

"""
`Dimensions` refers to the structural properties of a grid, 
    matrix, or layout, specifying the number of columns and 
    rows into which the grid is partitioned.
`Size` denotes the physical or spatial extent of an object,
    characterized by its width and height. These measurements
    are typically expressed in pixels, but any unit of physical 
    distance may be employed.
"""
Dimensions = namedtuple("Dimensions", "rows cols")
Size = namedtuple("Size", "width height")

# Type definitions.
type RGBColor = tuple[int, int, int]

# Determines the ratio between the PyGame window resolution and the screen resolution
WINDOW_SIZE_SCREEN_FRACTION = 0.95
