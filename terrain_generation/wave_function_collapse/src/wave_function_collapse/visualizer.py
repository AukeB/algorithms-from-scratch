"""Module for visualizing the Wave Function Collapse algorithm using pygame."""

import math

import pygame as pg
import random as rd

from src.wave_function_collapse.config_manager import ConfigModel
from src.wave_function_collapse.tile import Tile
from src.wave_function_collapse.grid_cell import GridCell
from src.wave_function_collapse.utils.utils_pygame import (
    get_window_size_from_screen_resolution,
)
from src.wave_function_collapse.constants import Size, RGBColor


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
        grid_dimensions: Size,
        tile_dimensions: Size,
        color_mapping: dict[RGBColor, str],
        margin_size: int = 20,
    ) -> None:
        """
        Initialise pygame and configure the visualizer for the given grid.

        Args:
            config (ConfigModel): The validated configuration model.
            grid_dimensions (Size): The width and height of the output grid in tiles.
            tile_dimensions (Size): The width and height of each tile in cells.
            color_mapping (dict[RGBColor, str]): A dict mapping characters to RGB tuples.
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
            (tuple[Size, Size]): A tuple of (tile_size, cell_size) in pixels.
        """
        tile_size = Size(
            int(
                (self.screen_size.height - 2 * self.margin_size)
                / self.grid_dimensions.height
            )
            if square_grid
            else int(
                (self.screen_size.width - 2 * self.margin_size)
                / self.grid_dimensions.width
            ),
            int(
                (self.screen_size.height - 2 * self.margin_size)
                / self.grid_dimensions.height
            ),
        )

        cell_size = Size(
            int((tile_size.width - inner_margin) / self.tile_dimensions.width),
            int((tile_size.height - inner_margin) / self.tile_dimensions.height),
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

        for row_tile_idx in range(self.grid_dimensions.height):
            for col_tile_idx in range(self.grid_dimensions.width):
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

    def show_tiles(self, tiles: dict[Tile, float] | list[Tile]) -> None:
        """
        Display all extracted tiles in a square grid layout for inspection.

        Accepts either a tile weights dict or a plain list of tiles. The grid
        dimensions are computed as the smallest square that fits all tiles.

        1. Normalise the input to a list of tiles.
        2. Compute the smallest square grid that fits all tiles.
        3. Recompute tile and cell sizes for the new grid dimensions.
        4. Draw each tile at its grid position, leaving empty cells for any
           remainder positions in the last row.
        5. Flip the display and block until the window is closed.

        Args:
            tiles (dict[Tile, float] | list[Tile]): Either a tile weights dict
                or a plain list of Tile instances to display.
        """
        if isinstance(tiles, dict):
            tiles = list(tiles.keys())

        next_square_number = math.ceil(math.sqrt(len(tiles)))
        self.grid_dimensions = Size(next_square_number, next_square_number)
        self.tile_size, self.cell_size = self._compute_tile_and_cell_size(
            inner_margin=3
        )

        for row_tile_idx in range(self.grid_dimensions.height):
            for col_tile_idx in range(self.grid_dimensions.width):
                x, y = self._compute_tile_position(row_tile_idx, col_tile_idx)
                index = row_tile_idx * self.grid_dimensions.height + col_tile_idx

                if index >= len(tiles):
                    continue

                self._draw_tile(tiles[index], x, y)

        pg.display.flip()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    break

    def show_neighbors(self, neighbors: dict[Tile, dict[str, set[Tile]]]) -> None:
        """
        Display the valid neighbors of a randomly selected tile for each direction.

        Selects a tile at random from the neighbors dict, then renders it on the
        left alongside its valid neighbors grouped by direction. Intended as a
        debug tool for verifying adjacency rules.

        1. Select a random tile from the neighbors dict.
        2. Compute a grid tall enough to fit the largest neighbor set.
        3. Recompute tile and cell sizes for the new grid dimensions.
        4. Draw the selected tile in the center-left of the screen.
        5. Draw each direction label and its neighbor tiles in columns to the right.
        6. Flip the display and block until the window is closed.

        Args:
            neighbors (dict[Tile, dict[str, set[Tile]]]): The full neighbor lookup
                produced by WaveFunctionCollapse._compute_neighbors().
        """
        pg.font.init()
        font = pg.font.SysFont("Arial", 36)

        self.screen.fill((255, 255, 255))

        key_to_check = rd.choice(list(neighbors.keys()))

        grid_height = max(
            (len(value) for value in neighbors[key_to_check].values()),
            default=7,
        )
        self.grid_dimensions = Size(
            self.screen_size.width // (self.screen_size.height // grid_height),
            grid_height,
        )
        self.tile_size, self.cell_size = self._compute_tile_and_cell_size(
            inner_margin=3
        )

        # Draw the selected tile on the left.
        x, y = self._compute_tile_position((self.grid_dimensions.height - 1) / 2, 0)
        self._draw_tile(key_to_check, x, y)  # type: ignore

        # Draw each direction label and its neighbor tiles in columns.
        for i, direction in enumerate(neighbors[key_to_check].keys()):
            x, y = self._compute_tile_position(i * 2 + (1 / 3), 2)
            text = font.render(direction.capitalize(), True, (0, 0, 0))
            self.screen.blit(text, (y, x))

            for j, neighbor_tile in enumerate(neighbors[key_to_check][direction]):
                x, y = self._compute_tile_position(i * 2, 4 + j)
                try:
                    self._draw_tile(neighbor_tile, x, y)  # type: ignore
                except Exception:
                    pass

        pg.display.flip()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    break
