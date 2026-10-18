"""Shared pytest fixtures. PyGame runs headless so the tests can open windows without a monitor."""

import json
import os
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pygame as pg
import pytest

# Run numba-compiled kernels as plain Python during tests, so coverage can trace them. Must be set
# before water_ripples is imported, which happens when the test modules are collected.
os.environ.setdefault("NUMBA_DISABLE_JIT", "1")


@pytest.fixture(scope="session", autouse=True, name="headless_pygame")
def fixture_headless_pygame() -> None:
    """Use the dummy SDL drivers, so windows and audio work without hardware."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(name="image_files")
def fixture_image_files(tmp_path: Path) -> dict[str, Path]:
    """Write a small image, mask and polygon, so tests never touch the real data folder.

    Args:
        tmp_path (Path): Pytest's per-test temporary folder.

    Returns:
        image_files (dict[str, Path]): Paths to the "image", "mask" and "polygon" files.
    """
    image_path = tmp_path / "image.png"
    mask_path = tmp_path / "mask.npy"
    polygon_path = tmp_path / "polygon.json"

    image = pg.Surface((400, 250))
    image.fill((30, 60, 90))
    pg.image.save(image, str(image_path))

    mask = np.ones((250, 400), dtype=bool)
    np.save(mask_path, mask)

    normalized_polygon = [[0.1, 0.1], [0.9, 0.1], [0.5, 0.9]]
    polygon_path.write_text(json.dumps(normalized_polygon))

    image_files = {"image": image_path, "mask": mask_path, "polygon": polygon_path}

    return image_files


@pytest.fixture(name="config_data")
def fixture_config_data(image_files: dict[str, Path]) -> dict[str, Any]:
    """Provide a small, valid raw configuration that tests can modify.

    Args:
        image_files (dict[str, Path]): The temporary image, mask and polygon files.

    Returns:
        config_data (dict[str, Any]): Raw configuration matching config.yaml.
    """
    config_data: dict[str, Any] = {
        "variant": "baseline",
        "window": {"window_width": 320, "window_height": 200},
        "simulation": {
            "number_of_columns": 16,
            "damping": 0.99,
            "wave_brightness": 255,
            "maximum_brightness": 255,
            "cursor_splash_size": 1,
            "framerate": 1000,
            "background_color": [0, 0, 0],
        },
        "baseline": {
            "render_mode": "surfarray",
            "rgb_mode": "scaled_colormap",
            "propagate_mode": "numba",
        },
        "trapezoid": {
            "y_top": 0.4,
            "y_bottom": 1.0,
            "x_top_left": 0.0,
            "x_top_right": 1.0,
            "x_bottom_left": 0.2,
            "x_bottom_right": 1.0,
            "perspective_exponent": 1.0,
        },
        "image": {
            "image_path": str(image_files["image"]),
            "mask_path": str(image_files["mask"]),
            "polygon_path": str(image_files["polygon"]),
            "reference_width": 400,
            "reference_height": 250,
            "perspective_start": 0.5,
        },
    }

    return config_data


@pytest.fixture(name="scripted_input")
def fixture_scripted_input(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., None]:
    """Feed PyGame input from a script instead of the real keyboard and mouse.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest's patching helper.

    Returns:
        script (Callable[..., None]): Call it with one list of events per frame, the mouse button
            state and the mouse position.
    """

    def script(
        event_batches: list[list[pg.event.Event]],
        mouse_pressed: bool = False,
        mouse_pos: tuple[int, int] = (0, 0),
    ) -> None:
        """Replace the PyGame input functions with the scripted values.

        Args:
            event_batches (list[list[pg.event.Event]]): The events returned by each frame, in
                order. A frame past the end of the script raises StopIteration.
            mouse_pressed (bool): Whether the left mouse button is held.
            mouse_pos (tuple[int, int]): The mouse position.
        """
        batches = iter(event_batches)

        monkeypatch.setattr(pg.event, "get", lambda: next(batches))
        monkeypatch.setattr(
            pg.mouse, "get_pressed", lambda num_buttons=3: (mouse_pressed, False, False)
        )
        monkeypatch.setattr(pg.mouse, "get_pos", lambda: mouse_pos)

    return script
