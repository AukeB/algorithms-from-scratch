"""Module for the configuration schema of the Voronoi diagram project."""

from pydantic import BaseModel, ConfigDict

from voronoi_diagram.constants import RGBColor


class ConfiguredBaseModel(BaseModel):
    """Config that disallows extra parameters not explicitly defined."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Config that combines all parameters."""

    class ConfigGame(ConfiguredBaseModel):
        """Config for the general game loop.

        Attributes:
            fps (int): Target frames per second.
        """

        fps: int

    class ConfigWindow(ConfiguredBaseModel):
        """Config for the window appearance.

        Attributes:
            caption (str): Window title.
            background_color (RGBColor): Color behind the grid.
            margin_size (int): Pixel margin between the window edge and the grid.
        """

        caption: str
        background_color: RGBColor
        margin_size: int

    class ConfigGrid(ConfiguredBaseModel):
        """Config for the grid dimensions and appearance.

        Attributes:
            dim (int): Number of cells along the width and height of the grid.
            show_gridlines (bool): Whether to draw lines between cells.
            grid_line_color (RGBColor): Color of the grid lines.
            grid_line_width (int): Width of the grid lines in pixels.
        """

        dim: int
        show_gridlines: bool
        grid_line_color: RGBColor
        grid_line_width: int

    class ConfigVoronoi(ConfiguredBaseModel):
        """Config for the Voronoi diagram.

        Attributes:
            num_seeds (int): Number of seed points, each one owning a region.
            seed_point_radius (int): Radius of the seed point markers in pixels.
        """

        num_seeds: int
        seed_point_radius: int

    game: ConfigGame
    window: ConfigWindow
    grid: ConfigGrid
    voronoi: ConfigVoronoi
