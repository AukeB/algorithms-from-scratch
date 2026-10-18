"""Module for the configuration schema of the Perlin noise algorithm."""

from pydantic import BaseModel, ConfigDict

from perlin_noise.constants import RGBColor, SmoothingVersion


class ConfiguredBaseModel(BaseModel):
    """Config that disallows extra parameters not explicitly defined."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Schema for all settings loaded from config.yaml."""

    class GridConfig(ConfiguredBaseModel):
        """Schema for grid initialization settings.

        Attributes:
            dim (int): Number of cells along each side of the grid.
            cell_resolution (int): Number of samples per cell along one dimension.
            random_seed (int | None): Seed for reproducible gradients, or None.
            smoothing_version (str): "original" or "revised" smoothing curve.
        """

        dim: int
        cell_resolution: int
        random_seed: int | None
        smoothing_version: SmoothingVersion

    class VisualizationConfig(ConfiguredBaseModel):
        """Schema for visualization settings.

        Attributes:
            margin_size (int): Pixel margin around the grid on all sides.
            arrow_length (float): Length of gradient arrows, in grid cells.
            background_color (RGBColor): Background color of the window.
            grid_line_color (RGBColor): Color of the grid lines.
            circle_color (RGBColor): Color of the grid nodes.
            arrow_color (RGBColor): Color of the gradient arrows.
            heatmap_positive_color (RGBColor): Color for the largest positive noise.
            heatmap_negative_color (RGBColor): Color for the most negative noise.
            grid_line_width (int): Width of the grid lines in pixels.
            circle_width (int): Radius of the grid nodes in pixels.
            arrow_width (int): Width of the gradient arrows in pixels.
        """

        margin_size: int
        arrow_length: float
        background_color: RGBColor
        grid_line_color: RGBColor
        circle_color: RGBColor
        arrow_color: RGBColor
        heatmap_positive_color: RGBColor
        heatmap_negative_color: RGBColor

        grid_line_width: int
        circle_width: int
        arrow_width: int

    grid: GridConfig
    visualization: VisualizationConfig
