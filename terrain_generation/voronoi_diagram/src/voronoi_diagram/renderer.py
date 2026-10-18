"""Module for the pygame window setup and rendering of the Voronoi diagram."""

import logging

import pygame as pg

from voronoi_diagram.config_model import ConfigModel
from voronoi_diagram.constants import RGBColor, Size
from voronoi_diagram.grid import Grid
from voronoi_diagram.utils.utils_colors import generate_voronoi_colors
from voronoi_diagram.utils.utils_pygame import get_window_size_from_screen_resolution

logger = logging.getLogger(__name__)


class Renderer:
    """Manage the pygame window and draw each frame of the Voronoi diagram.

    Attributes:
        window_background_color (RGBColor): Color behind the grid.
        margin_size (int): Pixel margin between the window edge and the grid, after snapping.
        show_gridlines (bool): Whether to draw lines between cells.
        grid_line_color (RGBColor): Color of the grid lines.
        grid_line_width (int): Width of the grid lines in pixels.
        grid_dim (int): Number of cells along each side of the grid.
        seed_point_radius (int): Radius of the seed point markers in pixels.
        num_seeds (int): Number of seed points, and so of colors in each palette.
        screen_size (Size): Window size in pixels, after snapping.
        grid_size (int): Side length of the square grid in pixels, after snapping.
        cell_size (int): Side length of one grid cell in pixels, after snapping.
        screen (pg.Surface): The PyGame window surface.
        clock (pg.time.Clock): Used to cap the frame rate.
        seed_point_colors (list[RGBColor]): Marker color for each seed point.
        voronoi_cell_colors (list[RGBColor]): Fill color for each seed point's region.

    Example:
        >>> renderer = Renderer(config=ConfigManager().load_config_file())
        >>> renderer.render(grid=grid)
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initialize pygame and open the window, sized so the grid fits exactly.

        Args:
            config (ConfigModel): The validated configuration model.
        """
        self.window_background_color = config.window.background_color
        self.margin_size = config.window.margin_size
        self.show_gridlines = config.grid.show_gridlines
        self.grid_line_color = config.grid.grid_line_color
        self.grid_line_width = config.grid.grid_line_width
        self.grid_dim = config.grid.dim
        self.seed_point_radius = config.voronoi.seed_point_radius
        self.num_seeds = config.voronoi.num_seeds

        pg.init()

        # The window size is chosen before the display opens. The grid is square, sized from the smaller
        # of the two margin-adjusted screen dimensions, and hugs the top-left corner.
        window_width, window_height = get_window_size_from_screen_resolution()
        self.screen_size = Size(width=window_width, height=window_height)

        grid_space = min(
            self.screen_size.width - 2 * self.margin_size,
            self.screen_size.height - 2 * self.margin_size,
        )
        self.grid_size = grid_space
        self.cell_size = self.grid_size / self.grid_dim

        self._snap_to_pixel_grid()

        self.screen = pg.display.set_mode(
            (self.screen_size.width, self.screen_size.height)
        )
        self.clock = pg.time.Clock()

        pg.display.set_caption(config.window.caption)

        seed_point_colors, voronoi_cell_colors = generate_voronoi_colors(
            num_seeds=self.num_seeds
        )
        self.seed_point_colors: list[RGBColor] = seed_point_colors
        self.voronoi_cell_colors: list[RGBColor] = voronoi_cell_colors

    def _snap_to_pixel_grid(self) -> None:
        """Round the cell size to whole pixels, and rescale the window to match.

        PyGame's Rect truncates float dimensions, which leaves sub-pixel gaps between cells. The cell
        size is rounded, and the window size and margin are scaled by the same ratio, so the grid
        still fills the available space exactly.
        """
        original_width = self.screen_size.width
        original_height = self.screen_size.height

        snap_ratio = round(self.cell_size) / self.cell_size
        self.cell_size = round(self.cell_size)
        self.margin_size = round(self.margin_size * snap_ratio)

        snapped_width = round(self.screen_size.width * snap_ratio)
        snapped_height = round(self.screen_size.height * snap_ratio)
        self.screen_size = Size(width=snapped_width, height=snapped_height)

        self.grid_size = self.cell_size * self.grid_dim

        adjustment_percent = (snap_ratio - 1) * 100
        logger.info(
            f"Cell-size snapping: window size adjusted from [{original_width}, "
            f"{original_height}] to [{self.screen_size.width}, "
            f"{self.screen_size.height}] ({adjustment_percent:+.2f}%) to keep cells "
            "pixel-aligned."
        )

    def tick(self, fps: int) -> None:
        """Wait so the loop runs at no more than the target frame rate.

        Args:
            fps (int): Target frames per second.
        """
        self.clock.tick(fps)

    def _draw_grid_lines(self) -> None:
        """Draw horizontal and vertical lines between the cells of the grid."""
        grid_end = int(self.margin_size + self.grid_size)

        for row in range(self.grid_dim + 1):
            y = int(self.margin_size + row * self.cell_size)
            start = (self.margin_size, y)
            end = (grid_end, y)
            pg.draw.line(self.screen, self.grid_line_color, start, end, self.grid_line_width)

        for col in range(self.grid_dim + 1):
            x = int(self.margin_size + col * self.cell_size)
            start = (x, self.margin_size)
            end = (x, grid_end)
            pg.draw.line(self.screen, self.grid_line_color, start, end, self.grid_line_width)

    def _draw_cells(self, grid: Grid) -> None:
        """Fill every cell with the color of the seed point that owns it.

        Args:
            grid (Grid): The grid whose cells are drawn.
        """
        for row in range(grid.dimensions.rows):
            for col in range(grid.dimensions.cols):
                owner = grid.cells[row][col]
                color = self.voronoi_cell_colors[owner]

                left = self.margin_size + col * self.cell_size
                top = self.margin_size + row * self.cell_size
                cell_rect = pg.Rect(left, top, self.cell_size, self.cell_size)

                pg.draw.rect(self.screen, color, cell_rect)

    def _draw_seed_points(self, grid: Grid) -> None:
        """Draw each seed point as a filled circle.

        Args:
            grid (Grid): The grid whose seed points are drawn.
        """
        for idx, seed in enumerate(grid.seed_points):
            x = int(self.margin_size + seed.x * self.cell_size)
            y = int(self.margin_size + seed.y * self.cell_size)
            center = (x, y)
            color = self.seed_point_colors[idx]

            pg.draw.circle(self.screen, color, center, self.seed_point_radius)

    def render(self, grid: Grid) -> None:
        """Draw one frame: the background, the cells, the seed points and optionally the grid lines.

        Args:
            grid (Grid): The grid to draw.
        """
        self.screen.fill(self.window_background_color)
        self._draw_cells(grid=grid)
        self._draw_seed_points(grid=grid)

        if self.show_gridlines:
            self._draw_grid_lines()

        pg.display.flip()

    def quit(self) -> None:
        """Shut down pygame."""
        pg.quit()
