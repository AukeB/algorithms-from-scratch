"""Shared pytest fixtures. PyGame runs headless so the tests can open windows without a monitor."""

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import openpyxl
import pygame as pg
import pytest
import yaml
from openpyxl.styles import Border, PatternFill, Side

from wave_function_collapse.config_model import ConfigModel
from wave_function_collapse.constants import CONFIG_FILE_PATH


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
    with open(CONFIG_FILE_PATH, encoding="utf-8") as file:
        raw_config: dict[str, Any] = yaml.safe_load(file)

    return raw_config


@pytest.fixture(name="small_config")
def fixture_small_config(raw_config: dict[str, Any]) -> ConfigModel:
    """Provide a validated config with a small grid, so the tests run quickly.

    Args:
        raw_config (dict[str, Any]): The raw config to modify and validate.

    Returns:
        config (ConfigModel): A 6 x 6 grid of 2 x 2 tiles, without image export.
    """
    raw_config["general"]["grid_dim"] = 6
    raw_config["general"]["tile_dim"] = 2
    raw_config["general"]["recursion_depth"] = 3
    raw_config["bitmap"]["export"] = False
    config = ConfigModel.model_validate(raw_config)

    return config


@pytest.fixture(name="stripe_bitmap")
def fixture_stripe_bitmap() -> list[list[str]]:
    """Provide a small two-colour bitmap with diagonal stripes.

    Returns:
        bitmap (list[list[str]]): A 4 x 4 bitmap of "A" and "B" characters.
    """
    bitmap = [
        ["A", "A", "B", "B"],
        ["A", "A", "B", "B"],
        ["B", "B", "A", "A"],
        ["B", "B", "A", "A"],
    ]

    return bitmap


@pytest.fixture(name="write_bitmap_xlsx")
def fixture_write_bitmap_xlsx() -> Callable[[Path, list[list[str]]], Path]:
    """Provide a helper that writes a bordered, filled .xlsx bitmap.

    Returns:
        write_bitmap_xlsx (Callable[[Path, list[list[str]]], Path]): Takes a folder and rows of hex
            colours, and returns the path of the written file.
    """

    def write(directory: Path, rows: list[list[str]]) -> Path:
        """Write the bitmap to a workbook, with a border around the cells it occupies.

        Args:
            directory (Path): Folder to write the workbook into.
            rows (list[list[str]]): Rows of 6-character hex colours.

        Returns:
            file_path (Path): The path of the written workbook.
        """
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        side = Side(style="thin")

        for row_index, hex_row in enumerate(rows, start=1):
            for col_index, color_hex in enumerate(hex_row, start=1):
                cell = worksheet.cell(row=row_index, column=col_index)
                cell.fill = PatternFill(
                    fill_type="solid", start_color=f"FF{color_hex}", end_color=f"FF{color_hex}"
                )
                cell.border = Border(
                    bottom=side if col_index == 1 else None,
                    right=side if row_index == 1 else None,
                )

        file_path = directory / "test_bitmap.xlsx"
        workbook.save(file_path)

        return file_path

    return write


@pytest.fixture(name="scripted_input")
def fixture_scripted_input(monkeypatch: pytest.MonkeyPatch) -> Callable[..., None]:
    """Feed PyGame events from a script instead of the real keyboard.

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
