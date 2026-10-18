"""Module for reading bitmaps from .xlsx files and exporting them as images."""

import logging
from pathlib import Path

from PIL import Image, ImageDraw

from wave_function_collapse.config_model import ConfigModel
from wave_function_collapse.constants import (
    BITMAPS_EXPORT_DIRECTORY_PATH,
    BITMAPS_INPUT_DIRECTORY_PATH,
    RGBColor,
)
from wave_function_collapse.utils.utils_excel import (
    detect_bitmap_dimensions,
    extract_bitmap_from_worksheet,
    load_excel_worksheet,
)

logger = logging.getLogger(__name__)

_FIRST_IDENTIFIER = "A"


class Bitmap:
    """Read a bitmap from an .xlsx file, and optionally export it as an image.

    Attributes:
        bitmap_dimensions (Dimensions): Number of rows and columns of the bitmap.
        bitmap (list[list[RGBColor]]): The bitmap as rows of RGB colours.

    Example:
        >>> bitmap_instance = Bitmap(config=ConfigManager().read_config())
        >>> bitmap_instance.bitmap[0][0]
        (0, 0, 0)
    """

    def __init__(
        self,
        config: ConfigModel,
        input_directory: Path = BITMAPS_INPUT_DIRECTORY_PATH,
        export_directory: Path = BITMAPS_EXPORT_DIRECTORY_PATH,
    ) -> None:
        """Load the bitmap, and export it as an image if the config asks for it.

        Args:
            config (ConfigModel): The validated configuration model.
            input_directory (Path): Folder that contains the .xlsx file.
            export_directory (Path): Folder the image export is written to.
        """
        input_file_name = config.bitmap.input_file_name
        input_file_path = input_directory / input_file_name

        worksheet = load_excel_worksheet(excel_file_path=input_file_path)
        self.bitmap_dimensions = detect_bitmap_dimensions(worksheet=worksheet)
        self.bitmap = extract_bitmap_from_worksheet(
            worksheet=worksheet,
            bitmap_dimensions=self.bitmap_dimensions,
        )

        if config.bitmap.export:
            export_file_name = input_file_name.stem + config.bitmap.export_file_format
            export_file_path = export_directory / export_file_name
            background_color = config.bitmap.background_color

            self.export_bitmap_as_image(
                export_file_path=export_file_path,
                cell_size=config.bitmap.cell_size,
                background_color=background_color,
            )

    def export_bitmap_as_image(
        self,
        export_file_path: Path,
        cell_size: int,
        background_color: RGBColor,
    ) -> None:
        """Save the bitmap as an image, with each bitmap cell drawn as a square of
        pixels.

        Args:
            export_file_path (Path): Where the image is written.
            cell_size (int): Width and height of one bitmap cell in pixels.
            background_color (RGBColor): Background colour of the image.
        """
        image_width = cell_size * self.bitmap_dimensions.cols
        image_height = cell_size * self.bitmap_dimensions.rows
        image = Image.new(
            mode="RGB",
            size=(image_width, image_height),
            color=background_color,
        )
        draw = ImageDraw.Draw(image)

        for row_index, bitmap_row in enumerate(self.bitmap):
            for col_index, color in enumerate(bitmap_row):
                left = col_index * cell_size
                top = row_index * cell_size
                right = left + cell_size - 1
                bottom = top + cell_size - 1

                draw.rectangle([left, top, right, bottom], fill=color)

        image.save(export_file_path)

        logger.info(f"Bitmap exported as {export_file_path}")

    def create_color_mapping(self, bitmap: list[list[RGBColor]]) -> dict[RGBColor, str]:
        """Give each distinct colour in the bitmap its own character, starting at "A".

        Args:
            bitmap (list[list[RGBColor]]): The bitmap as rows of RGB colours.

        Returns:
            color_mapping (dict[RGBColor, str]): Maps each distinct colour to a
                character.
        """
        color_mapping: dict[RGBColor, str] = {}

        for bitmap_row in bitmap:
            for cell_color in bitmap_row:
                if cell_color not in color_mapping:
                    next_code_point = ord(_FIRST_IDENTIFIER) + len(color_mapping)
                    identifier = chr(next_code_point)
                    color_mapping[cell_color] = identifier

        return color_mapping

    def apply_color_mapping(
        self,
        bitmap: list[list[RGBColor]],
        color_mapping: dict[RGBColor, str],
    ) -> list[list[str]]:
        """Replace each colour in the bitmap with its character.

        Args:
            bitmap (list[list[RGBColor]]): The bitmap as rows of RGB colours.
            color_mapping (dict[RGBColor, str]): Maps each colour to a character.

        Returns:
            mapped_bitmap (list[list[str]]): The bitmap as rows of characters.
        """
        mapped_bitmap = [[color_mapping[color] for color in row] for row in bitmap]

        return mapped_bitmap
