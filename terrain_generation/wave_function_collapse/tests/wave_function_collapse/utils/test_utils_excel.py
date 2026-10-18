"""Tests for the utils_excel module."""

from collections.abc import Callable
from pathlib import Path

import openpyxl
import pytest

from wave_function_collapse.constants import Dimensions
from wave_function_collapse.utils.utils_excel import (
    detect_bitmap_dimensions,
    extract_bitmap_from_worksheet,
    load_excel_worksheet,
)


# Testing the "load_excel_worksheet" function.


def test_load_excel_worksheet_returns_the_requested_sheet(
    tmp_path: Path, write_bitmap_xlsx: Callable[[Path, list[list[str]]], Path]
) -> None:
    file_path = write_bitmap_xlsx(tmp_path, [["FF0000"]])

    worksheet = load_excel_worksheet(excel_file_path=file_path, worksheet_index=0)

    assert worksheet.title == openpyxl.load_workbook(file_path).worksheets[0].title


# Testing the "detect_bitmap_dimensions" function.


def test_detect_bitmap_dimensions_reads_the_border(
    tmp_path: Path, write_bitmap_xlsx: Callable[[Path, list[list[str]]], Path]
) -> None:
    file_path = write_bitmap_xlsx(tmp_path, [["FF0000"] * 4] * 3)
    worksheet = load_excel_worksheet(excel_file_path=file_path)

    dimensions = detect_bitmap_dimensions(worksheet=worksheet)

    assert dimensions == Dimensions(rows=3, cols=4)


def test_detect_bitmap_dimensions_raises_without_border(tmp_path: Path) -> None:
    file_path = tmp_path / "empty.xlsx"
    openpyxl.Workbook().save(file_path)
    worksheet = load_excel_worksheet(excel_file_path=file_path)

    with pytest.raises(ValueError, match="Could not detect bitmap dimensions"):
        detect_bitmap_dimensions(worksheet=worksheet)


# Testing the "extract_bitmap_from_worksheet" function.


def test_extract_bitmap_from_worksheet_reads_fill_colours(
    tmp_path: Path, write_bitmap_xlsx: Callable[[Path, list[list[str]]], Path]
) -> None:
    file_path = write_bitmap_xlsx(tmp_path, [["FF0000", "00FF00"], ["0000FF", "FFFFFF"]])
    worksheet = load_excel_worksheet(excel_file_path=file_path)

    bitmap = extract_bitmap_from_worksheet(
        worksheet=worksheet, bitmap_dimensions=Dimensions(rows=2, cols=2)
    )

    assert bitmap == [[(255, 0, 0), (0, 255, 0)], [(0, 0, 255), (255, 255, 255)]]
