"""Project-specific constants."""

from collections import namedtuple
from pathlib import Path

# Paths.
CONFIG_FILE_PATH = Path("src/wave_function_collapse/configs/config.yaml")
BITMAPS_DIRECTORY_PATH = Path("src/wave_function_collapse/bitmaps/")

# Named tuples.
Size = namedtuple("Size", ["width", "height"])

# Type definitions.
type RGBColor = tuple[int, int, int]
type TileValue = tuple[tuple[str, ...], ...]

# Other constants.
DIRECTIONS: dict[str, list[int]] = {
    "up": [-1, 0],
    "down": [1, 0],
    "left": [0, -1],
    "right": [0, 1],
}

# Determines the ratio between the PyGame window resolution and the screen resolution
WINDOW_SIZE_SCREEN_FRACTION = 0.95
