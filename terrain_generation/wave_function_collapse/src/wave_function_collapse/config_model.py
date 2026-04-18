"""Module for the configuration schema definitions for the WFC algorithm."""

from pathlib import Path
from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, Field

RGBColor: TypeAlias = Annotated[list[int], Field(min_length=3, max_length=3)]
Size2D: TypeAlias = Annotated[list[int], Field(min_length=2, max_length=2)]


class ConfigModel(BaseModel):
    """Schema for all settings loaded from config.yaml."""

    class RuntimeConfig(BaseModel):
        """Schema for per-run settings that can change between executions."""

        file_name: Path
        grid_dim: int
        tile_dim: int
        recursion_depth: int

    class ModesConfig(BaseModel):
        """Schema for WFC algorithm mode settings."""

        mode_model: Literal["overlapping", "simple-tiled", "even-simpler-tiled"]
        mode_boundary_conditions: Literal[
            "wrap_around", "clamping", "mirroring", "noise"
        ]

    class BitmapConfig(BaseModel):
        """Schema for a single bitmap's static properties."""

        dimensions: Size2D

    class PngBitmapConfig(BaseModel):
        """Schema for PNG export settings applied to all bitmaps."""

        export: bool
        cell_size: int
        background_color: RGBColor

    runtime: RuntimeConfig
    modes: ModesConfig
    bitmaps: dict[str, BitmapConfig]
    png_bitmap: PngBitmapConfig
