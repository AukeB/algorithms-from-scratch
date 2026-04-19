"""Module for the configuration schema definitions for the WFC algorithm."""

from pathlib import Path
from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, Field

RGBColor: TypeAlias = Annotated[list[int], Field(min_length=3, max_length=3)]
Size2D: TypeAlias = Annotated[list[int], Field(min_length=2, max_length=2)]


class ConfigModel(BaseModel):
    """Schema for all settings loaded from config.yaml."""

    class GeneralConfig(BaseModel):
        """Schema for general per-run settings that can change between executions."""

        grid_dim: int
        tile_dim: int
        recursion_depth: int
        show_superposition: bool

    class BitmapConfig(BaseModel):
        """Schema for bitmap input and export settings."""

        input_file_name: Path
        export: bool
        export_file_format: str
        cell_size: int
        background_color: RGBColor

    class ModesConfig(BaseModel):
        """Schema for WFC algorithm mode settings."""

        mode_model: Literal["overlapping", "simple-tiled", "even-simpler-tiled"]
        mode_boundary_conditions: Literal[
            "wrap_around", "clamping", "mirroring", "noise"
        ]

    general: GeneralConfig
    bitmap: BitmapConfig
    modes: ModesConfig
