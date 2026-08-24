"""Module for pygame window setup and rendering."""

import pygame as pg

from src.eca.config_model import ConfigModel
from src.eca.constants import Size
from src.eca.grid import Grid
from src.eca.utils.utils_pygame import get_window_size_from_screen_resolution


class Renderer:
    """Manages the pygame window and draws each frame."""

    def __init__(self, config: ConfigModel) -> None:
        """Initializes the renderer with configuration.

        Args:
            config (ConfigModel): Pydantic-validated configuration model.
        """
        self.window_background_color = config.window.background_color
        self.margin_size = config.window.margin_size
        self.grid_color_map = config.grid.color_map
        self.show_gridlines = config.grid.show_gridlines
        self.grid_line_color = config.grid.grid_line_color
        self.grid_line_width = config.grid.grid_line_width
        self.grid_dim = config.grid.dim
        window_caption = config.window.caption

        pg.init()

        self.screen_size = Size(*get_window_size_from_screen_resolution())
        self.screen = pg.display.set_mode(
            (self.screen_size.width, self.screen_size.height)
        )
        self.clock = pg.time.Clock()

        pg.display.set_caption(window_caption)

        # Grid is always square: sized from the smaller of the two
        # margin-adjusted screen dimensions, and hugs the top-left corner.
        self.grid_size = min(
            self.screen_size.width - 2 * self.margin_size,
            self.screen_size.height - 2 * self.margin_size,
        )
        self.cell_size = self.grid_size / self.grid_dim

    def tick(self, fps: int) -> float:
        """Advances the frame clock and reports the elapsed time.

        Args:
            fps (int): Target frames per second to cap the loop at.

        Returns:
            dt (float): Time in seconds elapsed since the last frame.
        """
        dt = self.clock.tick(fps) / 1000

        return dt

    def _draw_grid_lines(self) -> None:
        """Draws horizontal and vertical grid lines across the grid area."""
        for row in range(self.grid_dim + 1):
            y = int(self.margin_size + row * self.cell_size)
            pg.draw.line(
                self.screen,
                self.grid_line_color,
                (self.margin_size, y),
                (int(self.margin_size + self.grid_size), y),
                self.grid_line_width,
            )

        for col in range(self.grid_dim + 1):
            x = int(self.margin_size + col * self.cell_size)
            pg.draw.line(
                self.screen,
                self.grid_line_color,
                (x, self.margin_size),
                (x, int(self.margin_size + self.grid_size)),
                self.grid_line_width,
            )

    def render_grid(self, grid: Grid) -> None:
        """Draws every cell of the grid onto the display surface.

        Args:
            grid (Grid): The grid whose cells will be drawn.
        """
        for row in range(grid.dimensions.rows):
            for col in range(grid.dimensions.cols):
                value = grid.grid[row][col]
                color = self.grid_color_map[value]

                rect = pg.Rect(
                    self.margin_size + col * self.cell_size,
                    self.margin_size + row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pg.draw.rect(self.screen, color, rect)

    def render(self, grid: Grid) -> None:
        """Draws the current frame and presents it to the display.

        1. Fill the screen with the window background color.
        2. Draw the grid cells on top.
        3. Draw the grid lines.
        4. Flip the display buffer to show the frame.

        Args:
            grid (Grid): The grid whose cells will be drawn.
        """
        self.screen.fill(self.window_background_color)
        self.render_grid(grid=grid)

        if self.show_gridlines:
            self._draw_grid_lines()

        pg.display.flip()

    def quit(self) -> None:
        """Shuts down pygame."""
        pg.quit()
