"""Module for visualizing the Wave Function Collapse algorithm using pygame."""

import pygame as pg

from src.wave_function_collapse.config_manager import ConfigModel
from src.wave_function_collapse.grid_cell import GridCell
from src.wave_function_collapse.utils.utils_pygame import (
    get_window_size_from_screen_resolution,
)
from src.wave_function_collapse.constants import Size, Dimensions, RGBColor


class WFCVisualizer:
    """
    Renders the WFC grid and tile debug views to a pygame window.

    Handles all visual output for the algorithm, including the main grid
    visualization during collapse, a tile overview for inspecting extracted
    tiles and their weights, and a neighbor debug view for inspecting valid
    adjacencies per direction.
    """

    def __init__(
        self,
        config: ConfigModel,
        grid_dimensions: Dimensions,
        tile_dimensions: Dimensions,
        color_mapping: dict[RGBColor, str],
        margin_size: int = 20,
    ) -> None:
        """
        Initialise pygame and configure the visualizer for the given grid.

        Args:
            config (ConfigModel): The validated configuration model.
            grid_dimensions (Dimensions): The rows and columns of the output grid in tiles.
            tile_dimensions (Dimensions): The rows and columns of each tile in cells.
            color_mapping (dict[RGBColor, str]): A dict mapping RGB tuples to characters.
            margin_size (int): Pixel margin around the grid on all sides, defaults to 20.
        """
        pg.init()

        self.config = config
        self.screen_size = Size(*get_window_size_from_screen_resolution())
        self.grid_dimensions = grid_dimensions
        self.tile_dimensions = tile_dimensions
        self.margin_size = margin_size

        # Invert the color mapping so RGB tuples can be resolved back to characters.
        self.inverted_color_mapping = {v: k for k, v in color_mapping.items()}

        self.tile_size, self.cell_size = self._compute_tile_and_cell_size()
        self.screen = pg.display.set_mode(
            (self.screen_size.width, self.screen_size.height)
        )

    def _compute_tile_and_cell_size(
        self,
        inner_margin: int = 0,
        square_grid: bool = True,
    ) -> tuple[Size, Size]:
        """
        Compute the pixel dimensions of a single tile and a single cell.

        Tile size is derived from the available screen space divided by the
        grid dimensions. Cell size is the tile size divided by the tile
        dimensions, with an optional inner margin subtracted first.

        Args:
            inner_margin (int): Pixel margin subtracted from tile size before
                dividing into cells, defaults to 0.
            square_grid (bool): If True, tile width is derived from screen height
                to ensure square tiles regardless of aspect ratio, defaults to True.

        Returns:
            sizes (tuple[Size, Size]): A tuple of (tile_size, cell_size) in pixels.
        """
        tile_size = Size(
            int(
                (self.screen_size.height - 2 * self.margin_size)
                / self.grid_dimensions.rows
            )
            if square_grid
            else int(
                (self.screen_size.width - 2 * self.margin_size)
                / self.grid_dimensions.rows
            ),
            int(
                (self.screen_size.height - 2 * self.margin_size)
                / self.grid_dimensions.rows
            ),
        )

        cell_size = Size(
            int((tile_size.width - inner_margin) / self.tile_dimensions.rows),
            int((tile_size.height - inner_margin) / self.tile_dimensions.rows),
        )

        return tile_size, cell_size

    def _compute_tile_position(
        self, row_tile_idx: int | float, col_tile_idx: int | float
    ) -> tuple[int, int]:
        """
        Compute the pixel position of a tile's top-left corner on the screen.

        Args:
            row_tile_idx (int | float): The row index of the tile in the grid.
                Accepts float to support fractional positioning in debug views.
            col_tile_idx (int | float): The column index of the tile in the grid.
                Accepts float to support fractional positioning in debug views.

        Returns:
            position (tuple[int, int]): A (y, x) pixel position tuple.
        """
        y = self.margin_size + row_tile_idx * self.tile_size.height
        x = self.margin_size + col_tile_idx * self.tile_size.width

        position = (y, x)

        return position

    def _draw_tile(self, cell: GridCell, y: int, x: int) -> None:
        """
        Draw a single grid cell as a filled rectangle at pixel position (x, y).

        If the cell has not yet collapsed, the center pixel of its superposition
        tile is used as the fill color. If collapsed, the character at the center
        of the tile value is resolved to an RGB color via the inverted color mapping.

        Args:
            cell (GridCell): The grid cell to draw.
            y (int): The y pixel coordinate of the tile's top-left corner.
            x (int): The x pixel coordinate of the tile's top-left corner.
        """
        if cell.tile is None:
            cell_value = cell.superposition_tile[1][1]  # type: ignore
        else:
            cell_value = self.inverted_color_mapping[cell.tile.value[1][1]]

        cell_rect = pg.Rect(
            x,
            y,
            self.tile_size.width,
            self.tile_size.height,
        )

        pg.draw.rect(self.screen, cell_value, cell_rect)

    def visualize(self, grid: list[list[GridCell]]) -> None:
        """
        Render the current state of the WFC grid to the pygame window.

        Clears the screen, draws each grid cell at its computed pixel position,
        flips the display buffer to make the frame visible, then polls for quit
        events — exiting cleanly on window close or the Escape key.

        Args:
            grid (list[list[GridCell]]): The 2D grid of GridCell instances to render.
        """
        self.screen.fill((0, 0, 0))

        for row_tile_idx in range(self.grid_dimensions.rows):
            for col_tile_idx in range(self.grid_dimensions.rows):
                y_pixel, x_pixel = self._compute_tile_position(
                    row_tile_idx, col_tile_idx
                )
                cell = grid[row_tile_idx][col_tile_idx]
                self._draw_tile(cell, y_pixel, x_pixel)

        pg.display.flip()

        for event in pg.event.get():
            if (
                event.type == pg.QUIT
                or event.type == pg.KEYDOWN
                and event.key == pg.K_ESCAPE
            ):
                pg.quit()
                raise SystemExit
