"""Module for Pydantic configuration models."""

from pydantic import BaseModel, ConfigDict


class ConfiguredBaseModel(BaseModel):
    """Config that disallows extra parameters not explicitly defined"""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Config that combines all parameters"""

    class ConfigGame(ConfiguredBaseModel):
        """Config for general game loop parameters."""

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
        grid_line_color: list[int]
        grid_line_width: int  # Units: pixels.

    game: ConfigGame
    window: ConfigWindow
    grid: ConfigGrid
