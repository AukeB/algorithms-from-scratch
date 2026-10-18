"""Shared pytest fixtures. PyGame runs headless so the tests can open windows without a monitor."""

import os
from typing import Any, Callable

import pygame as pg
import pytest
import yaml

from voronoi_diagram.config_model import ConfigModel
from voronoi_diagram.constants import CONFIG_PATH


@pytest.fixture(scope="session", autouse=True, name="headless_pygame")
def fixture_headless_pygame() -> None:
    """Use the dummy SDL drivers, so windows and audio work without hardware."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(name="raw_config")
def fixture_raw_config() -> dict[str, Any]:
    """Provide the raw config.yaml content, which tests can modify.

    Returns:
        raw_config (dict[str, Any]): The parsed config file.
    """
    with open(CONFIG_PATH, encoding="utf-8") as file:
        raw_config: dict[str, Any] = yaml.safe_load(file)

    return raw_config


@pytest.fixture(name="small_config")
def fixture_small_config(raw_config: dict[str, Any]) -> ConfigModel:
    """Provide a validated config with a small grid, so the tests run quickly.

    Args:
        raw_config (dict[str, Any]): The raw config to modify and validate.

    Returns:
        config (ConfigModel): A 10 x 10 grid with 4 seed points.
    """
    raw_config["grid"]["dim"] = 10
    raw_config["voronoi"]["num_seeds"] = 4
    config = ConfigModel.model_validate(raw_config)

    return config


@pytest.fixture(name="scripted_input")
def fixture_scripted_input(monkeypatch: pytest.MonkeyPatch) -> Callable[..., None]:
    """Feed PyGame events from a script instead of the real keyboard and mouse.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest's patching helper.

    Returns:
        script (Callable[..., None]): Call it with one list of events per frame.
    """

    def script(event_batches: list[list[pg.event.Event]]) -> None:
        """Replace the PyGame event queue with the scripted batches.

        Args:
            event_batches (list[list[pg.event.Event]]): The events returned by each frame, in
                order. A frame past the end of the script raises StopIteration.
        """
        batches = iter(event_batches)

        monkeypatch.setattr(pg.event, "get", lambda: next(batches))

    return script
