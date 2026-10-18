"""Tests for the get_polygon_coordinates script."""

import importlib.util
import json
import logging
import runpy
from pathlib import Path
from typing import Any, Callable

import pygame as pg
import pytest

from water_ripples.config_manager import ConfigManager
from water_ripples.config_model import ConfigModel
from water_ripples.scripts.get_polygon_coordinates import (
    draw_picker,
    handle_event,
    run_picker,
)

_MODULE_NAME = "water_ripples.scripts.get_polygon_coordinates"


def _script_file(module_name: str) -> str:
    """Find the source file of a module, to run it as a script.

    Args:
        module_name (str): Dotted name of the module.

    Returns:
        origin (str): Path to the module's source file.
    """
    spec = importlib.util.find_spec(module_name)
    assert spec is not None and spec.origin is not None

    return spec.origin


# Testing the "handle_event" function.


@pytest.mark.parametrize(
    ("event", "start_points", "expected_action", "expected_points"),
    [
        (pg.event.Event(pg.QUIT), [], "quit", []),
        (pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE), [], "quit", []),
        (
            pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN),
            [(0, 0), (1, 0), (1, 1)],
            "save",
            [(0, 0), (1, 0), (1, 1)],
        ),
        (
            pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN),
            [(0, 0), (1, 0)],
            "continue",
            [(0, 0), (1, 0)],
        ),
        (
            pg.event.Event(pg.KEYDOWN, key=pg.K_z),
            [(0, 0), (1, 0)],
            "continue",
            [(0, 0)],
        ),
        (pg.event.Event(pg.KEYDOWN, key=pg.K_z), [], "continue", []),
        (pg.event.Event(pg.MOUSEBUTTONDOWN, button=1), [], "continue", [(7, 8)]),
        (pg.event.Event(pg.KEYDOWN, key=pg.K_a), [], "continue", []),
    ],
)
def test_handle_event_returns_expected_action(
    event: pg.event.Event,
    start_points: list[tuple[int, int]],
    expected_action: str,
    expected_points: list[tuple[int, int]],
) -> None:
    points = list(start_points)

    action = handle_event(event=event, points=points, mouse_pos=(7, 8))

    assert action == expected_action
    assert points == expected_points


# Testing the "draw_picker" function.


@pytest.mark.parametrize("point_count", [0, 1, 2, 3])
def test_draw_picker_draws_for_any_number_of_points(
    point_count: int, image_files: dict[str, Path]
) -> None:
    pg.init()
    pg.display.set_mode((400, 250))
    screen = pg.Surface((400, 250))
    font = pg.font.Font(None, 28)
    background = pg.image.load(image_files["image"]).convert()
    points = [(10 * (i + 1), 10 * (i + 1)) for i in range(point_count)]

    draw_picker(
        screen=screen,
        font=font,
        background=background,
        points=points,
        mouse_pos=(200, 125),
    )

    assert pg.surfarray.array3d(screen).max() > 0


# Testing the "run_picker" function.


def test_run_picker_saves_polygon_when_enter_is_pressed(
    image_files: dict[str, Path],
    scripted_input: Callable[..., None],
    tmp_path: Path,
) -> None:
    polygon_path = tmp_path / "polygon.json"
    scripted_input(
        event_batches=[
            [pg.event.Event(pg.MOUSEBUTTONDOWN, button=1)],
            [pg.event.Event(pg.MOUSEBUTTONDOWN, button=1)],
            [
                pg.event.Event(pg.MOUSEBUTTONDOWN, button=1),
                pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN),
            ],
        ],
        mouse_pos=(100, 50),
    )

    saved = run_picker(
        image_path=image_files["image"],
        polygon_path=polygon_path,
        reference_width=400,
        reference_height=250,
    )

    assert saved is True
    assert len(json.loads(polygon_path.read_text())) == 3


def test_run_picker_does_not_save_when_escape_is_pressed(
    image_files: dict[str, Path],
    scripted_input: Callable[..., None],
    tmp_path: Path,
) -> None:
    polygon_path = tmp_path / "unsaved_polygon.json"
    scripted_input(
        event_batches=[
            [pg.event.Event(pg.MOUSEBUTTONDOWN, button=1)],
            [pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE)],
        ],
    )

    saved = run_picker(
        image_path=image_files["image"],
        polygon_path=polygon_path,
        reference_width=400,
        reference_height=250,
    )

    assert saved is False
    assert not polygon_path.exists()


# Testing the "main" function, run as the script entry point.


@pytest.mark.parametrize(
    ("event_batches", "expects_file", "log_text"),
    [
        (
            [
                [pg.event.Event(pg.MOUSEBUTTONDOWN, button=1)],
                [pg.event.Event(pg.MOUSEBUTTONDOWN, button=1)],
                [
                    pg.event.Event(pg.MOUSEBUTTONDOWN, button=1),
                    pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN),
                ],
            ],
            True,
            "Saved polygon",
        ),
        ([[pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE)]], False, "Quit without saving"),
    ],
)
def test_main_runs_picker_from_configuration(
    config_data: dict[str, Any],
    scripted_input: Callable[..., None],
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    event_batches: list[list[pg.event.Event]],
    expects_file: bool,
    log_text: str,
) -> None:
    polygon_path = tmp_path / "saved_polygon.json"
    config_data["image"]["polygon_path"] = str(polygon_path)
    config = ConfigModel.model_validate(config_data)
    monkeypatch.setattr(ConfigManager, "load_config_file", lambda self: config)
    scripted_input(event_batches=event_batches, mouse_pos=(100, 50))

    with caplog.at_level(logging.INFO):
        runpy.run_path(_script_file(_MODULE_NAME), run_name="__main__")

    assert polygon_path.exists() is expects_file
    assert log_text in caplog.text
