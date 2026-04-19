"""Module for reading bitmap data from .xlsx files and exporting them as .png images."""

import logging

from pathlib import Path
from PIL import Image

from src.wave_function_collapse.config_manager import ConfigModel
from src.wave_function_collapse.utils.utils_excel import (
    load_excel_worksheet,
    detect_bitmap_dimensions,
    extract_bitmap_from_worksheet,
)
from src.wave_function_collapse.constants import (
    BITMAPS_INPUT_DIRECTORY_PATH,
    BITMAPS_EXPORT_DIRECTORY_PATH,
    RGBColor,
)


class Bitmap:
    """Handles reading bitmap data from .xlsx files and exporting them as images."""

    def __init__(self, config: ConfigModel) -> None:
        """
        Load the bitmap from the configured .xlsx file and optionally export it as an image.

        1. Resolve the input file path from the bitmaps input directory and configured file name.
        2. Load the worksheet and detect the bitmap dimensions from its borders.
        3. Extract the bitmap as a 2D list of RGB tuples.
        4. If export is enabled, export the bitmap as an image immediately.

        Args:
            config (ConfigModel): The validated configuration model.
        """
        input_file_name = config.bitmap.input_file_name
        bitmaps_input_directory_path = BITMAPS_INPUT_DIRECTORY_PATH
        input_file_path = bitmaps_input_directory_path / input_file_name

        worksheet = load_excel_worksheet(excel_file_path=input_file_path)
        self.bitmap_dimensions = detect_bitmap_dimensions(worksheet=worksheet)
        self.bitmap = extract_bitmap_from_worksheet(
            worksheet=worksheet, bitmap_dimensions=self.bitmap_dimensions
        )

        self.bitmap_export = config.bitmap.export

        # Settings that are needed when exporting the .xlsx file to an image.
        if self.bitmap_export:
            self.bitmap_export_file_format = config.bitmap.export_file_format
            self.bitmap_export_file_path = BITMAPS_EXPORT_DIRECTORY_PATH / Path(
                input_file_name.stem + self.bitmap_export_file_format
            )
            self.bitmap_cell_size = config.bitmap.cell_size
            self.bitmap_background_color = tuple(config.bitmap.background_color)

            self.export_bitmap_as_image()

    def export_bitmap_as_image(self) -> None:
        """
        Export the bitmap as a scaled image file.

        1. Determine the output image dimensions by scaling the bitmap dimensions by cell size.
        2. Create a blank RGB image filled with the configured background color.
        3. Write each bitmap color into the corresponding block of pixels.
        4. Save the image to the configured export path.
        5. Log the output path.
        """
        img_width = self.bitmap_cell_size * self.bitmap_dimensions.cols
        img_height = self.bitmap_cell_size * self.bitmap_dimensions.rows

        image = Image.new(
            mode="RGB",
            size=(img_width, img_height),
            color=tuple(self.bitmap_background_color),
        )

        for y, bitmap_row in enumerate(self.bitmap):
            for x, color in enumerate(bitmap_row):
                for dx in range(self.bitmap_cell_size):
                    for dy in range(self.bitmap_cell_size):
                        image.putpixel(
                            (
                                x * self.bitmap_cell_size + dx,
                                y * self.bitmap_cell_size + dy,
                            ),
                            color,
                        )

        image.save(self.bitmap_export_file_path)

        logging.info(f"Bitmap exported as {self.bitmap_export_file_path}")

    def create_color_mapping(self, bitmap: list[list[RGBColor]]) -> dict[RGBColor, str]:
        """
        Assign a unique single character to each distinct color in the bitmap.

        1. Iterate over every color in the bitmap row by row.
        2. If the color has not been seen before, map it to the current character.
        3. Advance the character by one Unicode codepoint for the next new color.
        4. Return the completed color-to-character mapping.

        Args:
            bitmap (list[list[RGBColor]]): A 2D list of RGB tuples representing
                the bitmap.

        Returns:
            color_mapping (dict[RGBColor, str]): A dict mapping each unique RGB
                tuple to a distinct character.
        """
        color_mapping: dict[RGBColor, str] = {}
        current_char = "A"

        for bitmap_row in bitmap:
            for cell_color in bitmap_row:
                if cell_color not in color_mapping:
                    color_mapping[cell_color] = current_char
                    # chr() converts an integer codepoint back to a character, and ord() does the reverse.
                    # Together they increment the current character by one Unicode codepoint, e.g. 'A' -> 'B' -> 'C'.
                    # This would fail if the number of distinct colors exceeded the Unicode ceiling (~1.1M),
                    current_char = chr(ord(current_char) + 1)

        return color_mapping

    def apply_color_mapping(
        self,
        bitmap: list[list[RGBColor]],
        color_mapping: dict[RGBColor, str],
    ) -> list[list[str]]:
        """
        Replace each RGB tuple in the bitmap with its mapped character.

        Args:
            bitmap (list[list[RGBColor]]): A 2D list of RGB tuples representing the bitmap.
            color_mapping (dict[RGBColor, str]): A dict mapping RGB tuples to characters.

        Returns:
            mapped_bitmap (list[list[str]]): A 2D list of characters representing the color-mapped bitmap.
        """
        mapped_bitmap = [[color_mapping[color] for color in row] for row in bitmap]

        return mapped_bitmap
