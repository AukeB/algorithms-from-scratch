"""Tests for the bitmap module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from wave_function_collapse.bitmap import Bitmap
from wave_function_collapse.config_model import ConfigModel

_ROWS = [["FF0000", "00FF00"], ["0000FF", "FF0000"]]


@pytest.fixture(name="bitmap_directory")
def fixture_bitmap_directory(
    tmp_path: Path, write_bitmap_xlsx: Callable[[Path, list[list[str]]], Path]
) -> Path:
    """Write the test workbook into its own folder.

    Args:
        tmp_path (Path): Pytest's per-test temporary folder.
        write_bitmap_xlsx (Callable[[Path, list[list[str]]], Path]): Writes a bordered workbook.

    Returns:
        input_directory (Path): The folder that holds the workbook.
    """
    input_directory = tmp_path / "input"
    input_directory.mkdir()
    write_bitmap_xlsx(input_directory, _ROWS)

    return input_directory


# Testing the "__init__" method from the "Bitmap" class.


def test_init_reads_the_bitmap_without_exporting(
    small_config: ConfigModel, bitmap_directory: Path, tmp_path: Path
) -> None:
    export_directory = tmp_path / "export"
    export_directory.mkdir()
    bitmap_instance = Bitmap(
        config=_with_input(small_config, "test_bitmap.xlsx"),
        input_directory=bitmap_directory,
        export_directory=export_directory,
    )

    assert tuple(bitmap_instance.bitmap_dimensions) == (2, 2)
    assert bitmap_instance.bitmap == [[(255, 0, 0), (0, 255, 0)], [(0, 0, 255), (255, 0, 0)]]
    assert list(export_directory.iterdir()) == []


def test_init_exports_an_image_when_configured(
    small_config: ConfigModel, bitmap_directory: Path, tmp_path: Path, raw_config: dict[str, Any]
) -> None:
    raw_config["bitmap"]["export"] = True
    raw_config["bitmap"]["input_file_name"] = "test_bitmap.xlsx"
    raw_config["bitmap"]["cell_size"] = 4
    raw_config["bitmap"]["export_file_format"] = ".png"
    config = ConfigModel.model_validate(raw_config)

    Bitmap(config=config, input_directory=bitmap_directory, export_directory=tmp_path)

    exported = Image.open(tmp_path / "test_bitmap.png")
    assert exported.size == (8, 8)
    assert exported.getpixel((0, 0)) == (255, 0, 0)
    assert exported.getpixel((4, 0)) == (0, 255, 0)


# Testing the "export_bitmap_as_image" method from the "Bitmap" class.


def test_export_bitmap_as_image_scales_cells_to_squares(
    small_config: ConfigModel, bitmap_directory: Path, tmp_path: Path
) -> None:
    bitmap_instance = Bitmap(
        config=_with_input(small_config, "test_bitmap.xlsx"),
        input_directory=bitmap_directory,
        export_directory=tmp_path,
    )
    export_path = tmp_path / "scaled.png"

    bitmap_instance.export_bitmap_as_image(
        export_file_path=export_path, cell_size=3, background_color=(9, 9, 9)
    )

    exported = Image.open(export_path)
    assert exported.size == (6, 6)
    assert exported.getpixel((2, 5)) == (0, 0, 255)


# Testing the "create_color_mapping" method from the "Bitmap" class.


def test_create_color_mapping_gives_each_colour_a_letter_in_order(
    small_config: ConfigModel, bitmap_directory: Path, tmp_path: Path
) -> None:
    bitmap_instance = Bitmap(
        config=_with_input(small_config, "test_bitmap.xlsx"),
        input_directory=bitmap_directory,
        export_directory=tmp_path,
    )

    color_mapping = bitmap_instance.create_color_mapping(bitmap=bitmap_instance.bitmap)

    assert color_mapping == {(255, 0, 0): "A", (0, 255, 0): "B", (0, 0, 255): "C"}


# Testing the "apply_color_mapping" method from the "Bitmap" class.


def test_apply_color_mapping_replaces_colours_with_characters(
    small_config: ConfigModel, bitmap_directory: Path, tmp_path: Path
) -> None:
    bitmap_instance = Bitmap(
        config=_with_input(small_config, "test_bitmap.xlsx"),
        input_directory=bitmap_directory,
        export_directory=tmp_path,
    )
    color_mapping = {(255, 0, 0): "A", (0, 255, 0): "B", (0, 0, 255): "C"}

    mapped = bitmap_instance.apply_color_mapping(
        bitmap=bitmap_instance.bitmap, color_mapping=color_mapping
    )

    assert mapped == [["A", "B"], ["C", "A"]]


def _with_input(config: ConfigModel, file_name: str) -> ConfigModel:
    """Return a copy of the config that reads the given input file.

    Args:
        config (ConfigModel): The configuration to copy.
        file_name (str): The input file name to use.

    Returns:
        updated_config (ConfigModel): The copy, with the input file name set.
    """
    updated_config = config.model_copy(deep=True)
    updated_config.bitmap.input_file_name = Path(file_name)

    return updated_config
