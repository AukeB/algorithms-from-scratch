"""Module for Pydantic configuration models."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConfiguredBaseModel(BaseModel):
    """Config that disallows extra parameters not explicitly defined"""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Config that combines all parameters"""

    class ConfigGame(ConfiguredBaseModel):
        """Config for general game loop parameters."""

        initialization_mode: (
            str  # Determines how the first row is generated/initialized.
        )
        boundary_mode: (
            str  # Determines how propagation is handled at the edges of the grid.
        )
        rule_set: int = Field(ge=0, le=255)
        fps: int

    class ConfigWindow(ConfiguredBaseModel):
        """Config for window appearance."""

        caption: str
        background_color: list[int]
        margin_size: int  # Units: pixels.

    class ConfigGrid(ConfiguredBaseModel):
        """Config for grid dimensions and appearance."""

        dim: int  # Number of cells in width as well as height direction.
        color_map: dict[int, list[int]]
        show_gridlines: bool
        grid_line_color: list[int]
        grid_line_width: int  # Units: pixels.

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
                ValueError: If dim is even.
            """
            if dim % 2 == 0:
                raise ValueError(f"``dim`` must be odd, got {dim}.")

            return dim

    game: ConfigGame
    window: ConfigWindow
    grid: ConfigGrid
