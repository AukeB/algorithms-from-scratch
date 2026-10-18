"""Module for pygame window setup and rendering."""

import logging

import pygame as pg

from eca.config.config_model import ConfigModel
from eca.constants import Size
from eca.grid import Grid
from eca.utils.utils_pygame import get_window_size_from_screen_resolution

logger = logging.getLogger(__name__)


class Renderer:
    """Manages the pygame window and draws each frame.

    Attributes:
        _window_background_color (list[int]): RGB color of the window
            background.
        _margin_size (int): Margin between the window edge and the grid, in
            pixels.
        _grid_color_map (dict[int, list[int]]): RGB color for each cell value.
        _show_gridlines (bool): Whether grid lines are drawn.
        _grid_line_color (list[int]): RGB color of the grid lines.
        _grid_line_width (int): Width of the grid lines, in pixels.
        _grid_dim (int): Number of cells in width as well as height direction.
        _screen_size (Size): Window width and height, in pixels.
        _grid_size (float): Width and height of the grid area, in pixels.
        _cell_size (float): Width and height of one cell, in pixels.
        _screen (pg.Surface): The pygame display surface.
        _clock (pg.time.Clock): Clock used to cap the frame rate.
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initializes the renderer with configuration.

        Args:
            config (ConfigModel): Pydantic-validated configuration model.
        """
        self._window_background_color: list[int] = config.window.background_color
        self._margin_size: int = config.window.margin_size
        self._grid_color_map: dict[int, list[int]] = config.grid.color_map
        self._show_gridlines: bool = config.grid.show_gridlines
        self._grid_line_color: list[int] = config.grid.grid_line_color
        self._grid_line_width: int = config.grid.grid_line_width
        self._grid_dim: int = config.grid.dim

        pg.init()

        # Get screen size, but don't open the PyGame display yet. Cell size is
        # a function of grid dimensions and window-grid margin, and is rarely
        # a whole number of pixels: pygame's Rect truncates float dimensions,
        # which leaves sub-pixel gaps between cells, visible as thin horizontal
        # and vertical lines. The block below snaps cell size to an integer
        # pixel and rescales window size accordingly before the display opens.
        window_size = get_window_size_from_screen_resolution()
        self._screen_size: Size = Size(*window_size)

        # Grid is always square: sized from the smaller of the two
        # margin-adjusted screen dimensions, and hugs the top-left corner.
        self._grid_size: float = min(
            self._screen_size.width - 2 * self._margin_size,
            self._screen_size.height - 2 * self._margin_size,
        )

        self._cell_size: float = self._grid_size / self._grid_dim

        self._snap_to_pixel_grid()

        screen_size = (self._screen_size.width, self._screen_size.height)
        self._screen: pg.Surface = pg.display.set_mode(screen_size)
        self._clock: pg.time.Clock = pg.time.Clock()

        pg.display.set_caption(config.window.caption)

    def _snap_to_pixel_grid(self, verbose: bool = True) -> None:
        """Snaps cell size to the nearest integer pixel.

        PyGame's Rect silently truncates float dimensions to integers on
        construction, which causes sub-pixel gaps to accumulate across rows and
        columns during rendering. Window size and margin are rescaled by the
        same ratio so the grid still fills the available space exactly, with no
        leftover gap on any edge. The resulting window size adjustment is logged
        at INFO level.

        Args:
            verbose (bool): Whether to log the window size adjustment.
        """
        original_screen_size = self._screen_size

        snap_ratio = round(self._cell_size) / self._cell_size
        self._cell_size = round(self._cell_size)
        self._margin_size = round(self._margin_size * snap_ratio)

        snapped_width = round(self._screen_size.width * snap_ratio)
        snapped_height = round(self._screen_size.height * snap_ratio)
        self._screen_size = Size(snapped_width, snapped_height)

        self._grid_size = self._cell_size * self._grid_dim

        if verbose:
            adjustment_pct = (snap_ratio - 1) * 100
            logger.info(
                f"[cell-size snapping] window size adjusted from "
                f"[{original_screen_size.width}, {original_screen_size.height}] to "
                f"[{self._screen_size.width}, {self._screen_size.height}] "
                f"({adjustment_pct:+.2f}%) to keep cells pixel-aligned"
            )

    def tick(self, fps: int) -> float:
        """Advances the frame clock and reports the elapsed time.

        Args:
            fps (int): Target frames per second to cap the loop at.

        Returns:
            dt (float): Time in seconds elapsed since the last frame.
        """
        dt = self._clock.tick(fps) / 1000

        return dt

    def _draw_grid_lines(self) -> None:
        """Draws horizontal and vertical grid lines across the grid area."""
        grid_end = int(self._margin_size + self._grid_size)

        for row in range(self._grid_dim + 1):
            y = int(self._margin_size + row * self._cell_size)
            start = (self._margin_size, y)
            end = (grid_end, y)
            pg.draw.line(
                self._screen,
                self._grid_line_color,
                start,
                end,
                self._grid_line_width,
            )

        for col in range(self._grid_dim + 1):
            x = int(self._margin_size + col * self._cell_size)
            start = (x, self._margin_size)
            end = (x, grid_end)
            pg.draw.line(
                self._screen,
                self._grid_line_color,
                start,
                end,
                self._grid_line_width,
            )

    def _render_grid(self, grid: Grid) -> None:
        """Draws every cell of the grid onto the display surface.

        Args:
            grid (Grid): The grid whose cells will be drawn.
        """
        for row in range(grid.dimensions.rows):
            for col in range(grid.dimensions.cols):
                value = grid.grid[row][col]
                color = self._grid_color_map[value]

                rect = pg.Rect(
                    self._margin_size + col * self._cell_size,
                    self._margin_size + row * self._cell_size,
                    self._cell_size,
                    self._cell_size,
                )
                pg.draw.rect(self._screen, color, rect)

    def render(self, grid: Grid) -> None:
        """Draws the current frame and presents it to the display.

        1. Fill the screen with the window background color.
        2. Draw the grid cells on top.
        3. Draw the grid lines.
        4. Flip the display buffer to show the frame.

        Args:
            grid (Grid): The grid whose cells will be drawn.
        """
        self._screen.fill(self._window_background_color)
        self._render_grid(grid=grid)

        if self._show_gridlines:
            self._draw_grid_lines()

        pg.display.flip()

    def quit(self) -> None:
        """Shuts down pygame."""
        pg.quit()
