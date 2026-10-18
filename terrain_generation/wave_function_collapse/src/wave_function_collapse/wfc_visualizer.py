"""Module for drawing the Wave Function Collapse grid with pygame."""

import pygame as pg

from wave_function_collapse.config_model import ConfigModel
from wave_function_collapse.constants import Dimensions, RGBColor, Size
from wave_function_collapse.grid_cell import GridCell
from wave_function_collapse.utils.utils_pygame import (
    get_window_size_from_screen_resolution,
)

_MARGIN_SIZE = 20


class WFCVisualizer:
    """Draw the state of the grid in a pygame window, one square per grid cell.

    Attributes:
        screen_size (Size): Window size in pixels.
        grid_dimensions (Dimensions): Number of rows and columns of the output grid.
        tile_dimensions (Dimensions): Number of rows and columns of each tile.
        margin_size (int): Pixel margin around the grid.
        tile_size_px (int): Side length of one grid square in pixels.
        show_superposition (bool): Whether uncollapsed cells show their average colour.
        grid_background_color (RGBColor): Colour of uncollapsed cells when superposition
            is off.
        inverted_color_mapping (dict[str, RGBColor]): Maps each character to its colour.
        screen (pg.Surface): The PyGame window surface.

    Example:
        >>> visualizer = WFCVisualizer(config=config, color_mapping=color_mapping)
        >>> visualizer.visualize(grid=wfc.grid)
    """

    def __init__(
        self,
        config: ConfigModel,
        color_mapping: dict[RGBColor, str],
    ) -> None:
        """Open the window and size the grid squares to fit it.

        Args:
            config (ConfigModel): The validated configuration model.
            color_mapping (dict[RGBColor, str]): Maps each colour to its character.
        """
        pg.init()

        window_width, window_height = get_window_size_from_screen_resolution()
        self.screen_size = Size(width=window_width, height=window_height)
        self.grid_dimensions = Dimensions(
            rows=config.general.grid_dim,
            cols=config.general.grid_dim,
        )
        self.tile_dimensions = Dimensions(
            rows=config.general.tile_dim,
            cols=config.general.tile_dim,
        )
        self.margin_size = _MARGIN_SIZE
        self.show_superposition = config.general.show_superposition
        self.grid_background_color = config.general.grid_background_color

        self.inverted_color_mapping = {
            character: color for color, character in color_mapping.items()
        }

        available_height = self.screen_size.height - 2 * self.margin_size
        self.tile_size_px = int(available_height / self.grid_dimensions.rows)

        self.screen = pg.display.set_mode(
            (self.screen_size.width, self.screen_size.height)
        )

    def _compute_tile_position(
        self,
        row_index: float,
        col_index: float,
    ) -> tuple[int, int]:
        """Find the pixel position of the top-left corner of a grid square.

        Args:
            row_index (int | float): Row of the square in the grid.
            col_index (int | float): Column of the square in the grid.

        Returns:
            position (tuple[int, int]): The (y, x) pixel position.
        """
        y = self.margin_size + row_index * self.tile_size_px
        x = self.margin_size + col_index * self.tile_size_px
        position = (int(y), int(x))

        return position

    def _center_index(self) -> int:
        """Find the index of the centre cell of a tile.

        Returns:
            center_index (int): The row and column index of the centre cell.
        """
        center_index = self.tile_dimensions.rows // 2

        return center_index

    def _cell_color(self, cell: GridCell) -> RGBColor:
        """Choose the colour that represents a cell.

        A collapsed cell shows the colour at the centre of its tile. An uncollapsed cell
        shows the centre of its superposition if that is on, and the background colour
        otherwise.

        Args:
            cell (GridCell): The cell to colour.

        Returns:
            color (RGBColor): The colour of the cell.
        """
        center_index = self._center_index()

        if cell.tile is not None:
            center_character = cell.tile.value[center_index][center_index]
            color = self.inverted_color_mapping[center_character]
        elif self.show_superposition and cell.superposition_tile is not None:
            color = cell.superposition_tile[center_index][center_index]
        else:
            color = self.grid_background_color

        return color

    def _draw_tile(self, cell: GridCell, y: int, x: int) -> None:
        """Draw one grid square at a pixel position.

        Args:
            cell (GridCell): The cell whose square is drawn.
            y (int): Pixel row of the square's top-left corner.
            x (int): Pixel column of the square's top-left corner.
        """
        color = self._cell_color(cell=cell)
        square = pg.Rect(x, y, self.tile_size_px, self.tile_size_px)

        pg.draw.rect(self.screen, color, square)

    def _handle_events(self) -> bool:
        """Read the pending events. Closing the window or pressing ESC asks to stop.

        Returns:
            keep_running (bool): False if the user asked to stop, otherwise True.
        """
        keep_running = True

        for event in pg.event.get():
            if event.type == pg.QUIT or (
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                keep_running = False

        return keep_running

    def visualize(self, grid: list[list[GridCell]]) -> bool:
        """Draw the grid and show the frame, then read the events.

        Args:
            grid (list[list[GridCell]]): The grid to draw.

        Returns:
            keep_running (bool): False if the user asked to stop, otherwise True.
        """
        self.screen.fill((0, 0, 0))

        for row_index in range(self.grid_dimensions.rows):
            for col_index in range(self.grid_dimensions.cols):
                y, x = self._compute_tile_position(row_index, col_index)
                self._draw_tile(cell=grid[row_index][col_index], y=y, x=x)

        pg.display.flip()

        keep_running = self._handle_events()

        return keep_running

    def quit(self) -> None:
        """Shut down pygame."""
        pg.quit()
