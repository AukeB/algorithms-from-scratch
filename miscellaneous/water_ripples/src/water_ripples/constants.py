"""Module for storing project constants."""

from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "configs" / "config.yaml"

# Windowed size as a fraction of the desktop resolution (see screen.window_size_from_screen).
WINDOW_SIZE_SCREEN_FRACTION = 0.85
