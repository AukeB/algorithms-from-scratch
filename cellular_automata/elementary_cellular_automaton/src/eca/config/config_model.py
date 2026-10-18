"""Module for Pydantic configuration models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from eca.errors import EvenGridDimensionError


class ConfiguredBaseModel(BaseModel):
    """Config that disallows extra parameters not explicitly defined."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Config that combines all parameters.

    Attributes:
        game (ConfigGame): General game loop parameters.
        window (ConfigWindow): Window appearance.
        grid (ConfigGrid): Grid dimensions and appearance.
    """

    class ConfigGame(ConfiguredBaseModel):
        """Config for general game loop parameters.

        Attributes:
            initialization_mode (str): How the first row is generated, one of
                "single_alive_cell", "single_dead_cell", or "random".
            boundary_mode (str): How propagation is handled at the grid edges,
                one of "zero", "periodic", or "reflective".
            rule_set (int): Elementary cellular automaton rule, from 0 to 255.
            fps (int): Target frames per second.
        """

        initialization_mode: Literal["single_alive_cell", "single_dead_cell", "random"]

        boundary_mode: Literal["zero", "periodic", "reflective"]

        rule_set: int = Field(ge=0, le=255)
        fps: int

    class ConfigWindow(ConfiguredBaseModel):
        """Config for window appearance.

        Attributes:
            caption (str): Window title.
            background_color (list[int]): RGB color of the window background.
            margin_size (int): Margin between the window edge and the grid, in
                pixels.
        """

        caption: str
        background_color: list[int]
        margin_size: int

    class ConfigGrid(ConfiguredBaseModel):
        """Config for grid dimensions and appearance.

        Attributes:
            dim (int): Number of cells in width as well as height direction.
                Must be odd.
            color_map (dict[int, list[int]]): RGB color for each cell value.
            show_gridlines (bool): Whether grid lines are drawn.
            grid_line_color (list[int]): RGB color of the grid lines.
            grid_line_width (int): Width of the grid lines, in pixels.
        """

        dim: int
        color_map: dict[int, list[int]]
        show_gridlines: bool
        grid_line_color: list[int]
        grid_line_width: int

        @field_validator("dim")
        @classmethod
        def _validate_dim_is_odd(cls, dim: int) -> int:
            """Ensure the grid dimension is an odd number.

            An odd dimension guarantees a single, unambiguous center cell, which
            the initial-condition logic depends on.

            Args:
                dim (int): The proposed grid dimension.

            Returns:
                dim (int): The validated grid dimension.

            Raises:
                EvenGridDimensionError: If dim is even.
            """
            if dim % 2 == 0:
                raise EvenGridDimensionError(f"``dim`` must be odd, got {dim}.")

            return dim

    game: ConfigGame
    window: ConfigWindow
    grid: ConfigGrid
