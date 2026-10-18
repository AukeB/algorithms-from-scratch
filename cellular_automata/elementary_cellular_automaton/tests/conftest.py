"""Shared pytest fixtures for the test suite."""

import os
from typing import Any

import pytest

# Run pygame headless so the tests can open a display without a monitor.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture
def config_data() -> dict[str, Any]:
    """Provides a small, valid raw configuration that tests can modify.

    Returns:
        config_data (dict[str, Any]): Raw configuration matching config.yaml.
    """
    config_data: dict[str, Any] = {
        "game": {
            "initialization_mode": "single_alive_cell",
            "boundary_mode": "zero",
            "rule_set": 90,
            "fps": 10,
        },
        "window": {
            "caption": "Test",
            "background_color": [0, 0, 0],
            "margin_size": 20,
        },
        "grid": {
            "dim": 5,
            "color_map": {0: [0, 0, 0], 1: [255, 255, 255]},
            "show_gridlines": False,
            "grid_line_color": [128, 128, 128],
            "grid_line_width": 1,
        },
    }

    return config_data
