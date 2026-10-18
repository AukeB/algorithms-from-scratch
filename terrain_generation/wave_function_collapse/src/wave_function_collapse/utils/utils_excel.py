"""Module for reading bitmaps from Excel worksheets."""

from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from wave_function_collapse.constants import Dimensions, RGBColor
from wave_function_collapse.utils.utils_conversion import hex_to_rgb


def load_excel_worksheet(excel_file_path: Path, worksheet_index: int = 0) -> Worksheet:
    """Load an Excel file and return one of its worksheets.

    Args:
        excel_file_path (Path): Path to the .xlsx file to load.
        worksheet_index (int): Index of the worksheet to return. Defaults to the first
            one.

    Returns:
        worksheet (Worksheet): The worksheet at the given index.
    """
    workbook = load_workbook(excel_file_path)
    worksheet = workbook.worksheets[worksheet_index]

    return worksheet


def detect_bitmap_dimensions(worksheet: Worksheet) -> Dimensions:
    """Detect the size of a bitmap from the outer border drawn around it.

    The number of rows is the last row whose first-column cell has a bottom border. The
    number of columns is the last column whose first-row cell has a right border.

    Args:
        worksheet (Worksheet): The worksheet to scan.

    Returns:
        dimensions (Dimensions): The number of rows and columns of the bitmap.

    Raises:
        ValueError: If the worksheet has no bottom or right border to detect the bitmap
            from.
    """
    max_row = 0
    for row in range(1, worksheet.max_row + 1):
        bottom_border = worksheet.cell(row=row, column=1).border.bottom
        if bottom_border.border_style is not None:
            max_row = row

    max_col = 0
    for col in range(1, worksheet.max_column + 1):
        right_border = worksheet.cell(row=1, column=col).border.right
        if right_border.border_style is not None:
            max_col = col

    if max_row == 0 or max_col == 0:
        raise ValueError(
            f"Could not detect bitmap dimensions in worksheet '{worksheet.title}'. "
            "Ensure the bitmap has an outer border drawn around it in Excel."
        )

    dimensions = Dimensions(rows=max_row, cols=max_col)

    return dimensions


def extract_bitmap_from_worksheet(
    worksheet: Worksheet,
    bitmap_dimensions: Dimensions,
) -> list[list[RGBColor]]:
    """Read the fill colour of every bitmap cell.

    Args:
        worksheet (Worksheet): The worksheet to read.
        bitmap_dimensions (Dimensions): The number of rows and columns of the bitmap.

    Returns:
        bitmap (list[list[RGBColor]]): The bitmap as rows of RGB colours.
    """
    bitmap: list[list[RGBColor]] = []

    cell_rows = worksheet.iter_rows(
        min_row=1,
        max_row=bitmap_dimensions.rows,
        min_col=1,
        max_col=bitmap_dimensions.cols,
    )
    for cell_row in cell_rows:
        bitmap_row: list[RGBColor] = []

        for cell in cell_row:
            # The first two characters are the alpha channel, which is dropped.
            color_hex = cell.fill.start_color.index[2:]
            color_rgb = hex_to_rgb(color_hex=color_hex)
            bitmap_row.append(color_rgb)

        bitmap.append(bitmap_row)

    return bitmap
