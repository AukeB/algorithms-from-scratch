"""Module for the configuration schema definitions for the Perlin noise algorithm."""

from pydantic import BaseModel, ConfigDict

from src.perlin_noise.constants import RGBColor


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Schema for all settings loaded from config.yaml."""

    class GridConfig(ConfiguredBaseModel):
        """Schema for grid initialization settings."""

        dim: int
        cell_resolution: int
        random_seed: int | None

    class VisualizationConfig(ConfiguredBaseModel):
        """Schema for visualization settings."""

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
