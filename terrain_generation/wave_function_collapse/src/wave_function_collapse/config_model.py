"""Module for the configuration schema of the Wave Function Collapse algorithm."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ConfiguredBaseModel(BaseModel):
    """Config that disallows extra parameters not explicitly defined."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Config that combines all parameters."""

    class GeneralConfig(ConfiguredBaseModel):
        """Settings for the grid and the tiles.

        Attributes:
            grid_dim (int): Width and height of the output grid, in tiles.
            tile_dim (int): Width and height of each tile, in cells.
            recursion_depth (int): How many cells outward constraints propagate per
                collapse.
            show_superposition (bool): Whether uncollapsed cells show their average
                colour.
            grid_background_color (tuple[int, int, int]): Colour of uncollapsed cells
                when show_superposition is False.
        """

        grid_dim: int = Field(gt=0)
        tile_dim: int = Field(gt=0)
        recursion_depth: int = Field(ge=0)
        show_superposition: bool
        grid_background_color: tuple[int, int, int]

    class BitmapConfig(ConfiguredBaseModel):
        """Settings for the input bitmap and its image export.

        Attributes:
            input_file_name (Path): Name of the .xlsx file in the input bitmaps folder.
            export (bool): Whether to export the bitmap as an image.
            export_file_format (str): File extension of the exported image, such as
                .png.
            cell_size (int): Width and height of one bitmap cell in exported pixels.
            background_color (tuple[int, int, int]): Background colour of the exported
                image.
        """

        input_file_name: Path
        export: bool
        export_file_format: str
        cell_size: int = Field(gt=0)
        background_color: tuple[int, int, int]

    class ModesConfig(ConfiguredBaseModel):
        """Algorithm modes. Only the options marked as implemented can run.

        Attributes:
            mode_model (str): The tiling model. Only "overlapping" is implemented.
            mode_boundary_conditions (str): How the edges wrap. Only "wrap_around" is
                implemented.
        """

        mode_model: Literal["overlapping", "simple-tiled", "even-simpler-tiled"]
        mode_boundary_conditions: Literal[
            "wrap_around", "clamping", "mirroring", "noise"
        ]

    general: GeneralConfig
    bitmap: BitmapConfig
    modes: ModesConfig
