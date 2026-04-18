"""Module for the Wave Function Collapse algorithm."""

import time
import random as rd

from collections import defaultdict, Counter

from src.wave_function_collapse.config_manager import ConfigModel
from src.wave_function_collapse.tile import Tile
from src.wave_function_collapse.grid_cell import GridCell
from src.wave_function_collapse.visualizer import WFCVisualizer
from src.wave_function_collapse.constants import Size, RGBColor, DIRECTIONS


class WaveFunctionCollapse:
    """
    Implements the Wave Function Collapse algorithm on a 2D grid.

    The algorithm extracts all possible tiles and their frequencies from an
    input bitmap, then iteratively collapses grid cells to a single tile by
    choosing the cell with the lowest entropy, selecting a tile weighted by
    frequency, and propagating the resulting constraints to neighboring cells.
    """

    def __init__(
        self,
        config: ConfigModel,
        bitmap: list[list[str]],
        grid_dimensions: Size,
        tile_dimensions: Size,
        color_mapping: dict[RGBColor, str],
    ) -> None:
        """
        Initialise the WFC algorithm with the input bitmap and configuration.

        1. Store the config, bitmap, dimensions, and color mapping.
        2. Validate that the tile dimensions do not exceed the bitmap dimensions.
        3. Extract all tiles and their frequency weights from the bitmap.
        4. Compute the set of valid neighbors for each tile in each direction.
        5. Initialise the grid with all tiles as options for each cell.
        6. Initialise the visualizer.

        Args:
            config (ConfigModel): The validated configuration pydantic configuration model.
            bitmap (list[list[str]]): The color-mapped bitmap as a 2D list of characters.
            grid_dimensions (Size): The width and height of the output grid in tiles.
            tile_dimensions (Size): The width and height of each tile in cells.
            color_mapping (dict[RGBColor, str]): A dict mapping characters to RGB tuples.
        """
        self.config = config
        self.bitmap = bitmap
        self.bitmap_dimensions = Size(len(self.bitmap[0]), len(self.bitmap))
        self.grid_dimensions = grid_dimensions
        self.tile_dimensions = tile_dimensions
        self.recursion_depth = config.runtime.recursion_depth
        self.color_mapping = color_mapping

        self.directions = DIRECTIONS

        self._validate_tile_and_bitmap_dimensions()
        self.tile_weights, self.all_tiles = self._compute_tiles_and_weights()
        self.tile_set = set(self.tile_weights.keys())
        self.neighbors = self._compute_neighbors()
        self.grid = self._initialize_grid()

        self.wfc_visualizer = WFCVisualizer(
            config=config,
            grid_dimensions=self.grid_dimensions,
            tile_dimensions=tile_dimensions,
            color_mapping=self.color_mapping,
        )

        # #self.wfc_visualizer.show_tiles(self.all_tiles)
        # #self.wfc_visualizer.show_tiles(self.tile_weights)
        # self.wfc_visualizer.show_neighbors(self.neighbors)
        # To do: make a sort of test environment within pygame with buttons
        # something like: self.wfc_visualizer.test_environment()

    def _validate_tile_and_bitmap_dimensions(self) -> None:
        """
        Validate that the tile dimensions do not exceed the bitmap dimensions.

        Raises:
            ValueError: If either tile dimension is larger than the smallest
                bitmap dimension.
        """
        min_bitmap_dim = min(
            self.bitmap_dimensions.width, self.bitmap_dimensions.height
        )

        if (
            self.tile_dimensions.width > min_bitmap_dim
            or self.tile_dimensions.height > min_bitmap_dim
        ):
            raise ValueError(
                f"tile_size ({self.tile_dimensions}) must be smaller than or equal to the "
                f"minimum dimension of the bitmap (width: {self.bitmap_dimensions.width}, "
                f"height: {self.bitmap_dimensions.height})"
            )

    def _extract_tile(self, x: int, y: int) -> Tile:
        """
        Extract a tile from the bitmap at position (x, y) with wrapping.

        Wrapping ensures that tiles can be extracted from the edges of the
        bitmap without going out of bounds, treating the bitmap as a torus.

        Args:
            x (int): The column index of the top-left corner of the tile.
            y (int): The row index of the top-left corner of the tile.

        Returns:
            tile (Tile): The extracted tile at position (x, y).
        """
        tile_value = tuple(
            tuple(
                self.bitmap[(y + i) % self.bitmap_dimensions.height][
                    (x + j) % self.bitmap_dimensions.width
                ]
                for j in range(self.tile_dimensions.width)
            )
            for i in range(self.tile_dimensions.height)
        )

        tile = Tile(tile_value)

        return tile

    def _compute_tiles_and_weights(self) -> tuple[dict[Tile, float], list[Tile]]:
        """
        Extract all tiles from the bitmap and compute their frequency weights.

        Each tile's weight is its number of occurrences divided by the total
        number of tile positions in the bitmap, giving a normalized frequency.

        1. Count occurrences of each tile across all bitmap positions.
        2. Collect all extracted tiles in order.
        3. Normalise counts by total positions to produce frequency weights.
        4. Return the weights dict and the full ordered tile list.

        Returns:
            tile_weights, all_tiles (tuple[dict[TileValue, float], list[Tile]]):
                A tuple of the tile weights dict and the ordered list of all extracted tiles.
        """
        tile_count: Counter = Counter()
        total_occurrences = self.bitmap_dimensions.height * self.bitmap_dimensions.width

        all_tiles = []  # TODO: Maybe change to set ?

        for y in range(self.bitmap_dimensions.height):
            for x in range(self.bitmap_dimensions.width):
                tile = self._extract_tile(x, y)
                tile_count[tile] += 1
                all_tiles.append(tile)

        tile_weights = {
            tile: count / total_occurrences for tile, count in tile_count.items()
        }

        return tile_weights, all_tiles

    def _compute_neighbors(self) -> defaultdict:
        """
        Compute the set of valid neighboring tiles for each tile in each direction.

        Two tiles are valid neighbors in a direction if the overlapping slice of
        one tile matches the overlapping slice of the other. For example, a tile
        is a valid upward neighbor if its down slice matches the other tile's up slice.

        Returns:
            neighbors (defaultdict): A nested defaultdict mapping each tile to a
                dict of directions, each containing the set of valid neighbor tiles.
        """
        neighbors: defaultdict = defaultdict(lambda: defaultdict(set))

        for tile in self.tile_set:
            for other_tile in self.tile_set:
                if tile.up == other_tile.down:
                    neighbors[tile]["up"].add(other_tile)
                if tile.down == other_tile.up:
                    neighbors[tile]["down"].add(other_tile)
                if tile.left == other_tile.right:
                    neighbors[tile]["left"].add(other_tile)
                if tile.right == other_tile.left:
                    neighbors[tile]["right"].add(other_tile)

        return neighbors

    def _initialize_grid(self) -> list[list[GridCell]]:
        """
        Initialise the grid with a GridCell for each position, with all tiles as options.

        Returns:
            grid (list[list[GridCell]]): A 2D list of GridCell instances.
        """
        grid = [
            [
                GridCell(
                    tile_set=self.tile_set.copy(),
                    tile_weights=self.tile_weights,
                    color_mapping=self.color_mapping,
                )
                for _ in range(self.grid_dimensions.width)
            ]
            for _ in range(self.grid_dimensions.height)
        ]

        return grid

    def propagate(self, y: int, x: int, recursion_depth: int) -> None:
        """
        Recursively propagate tile constraints outward from cell (y, x).

        Starting from a collapsed or updated cell, this method intersects each
        neighbor's tile options with the set of tiles that are valid in that
        direction, then recurses into each updated neighbor. Recursion depth
        controls how far constraints spread in a single propagation pass.

        1. Return immediately if the recursion depth is exhausted.
        2. For each direction, compute the set of tiles valid in that direction.
        3. Intersect the neighbor's options with the valid set.
        4. Mark the neighbor as propagated and recompute its superposition tile.
        5. Recurse into the neighbor with a decremented recursion depth.
        6. Reset all propagated flags across the grid after the pass completes.

        Args:
            y (int): The row index of the source cell.
            x (int): The column index of the source cell.
            recursion_depth (int): The maximum number of recursive steps to take.
        """
        if recursion_depth <= 0:
            return

        for direction, (dy, dx) in self.directions.items():
            ny, nx = y + dy, x + dx

            if (
                0 <= nx < self.grid_dimensions.width
                and 0 <= ny < self.grid_dimensions.height
                and not self.grid[ny][nx].collapsed
                and not self.grid[ny][nx].propagated
            ):
                if self.grid[y][x].tile:
                    valid_tiles = self.neighbors.get(self.grid[y][x].tile, {}).get(
                        direction, set()
                    )
                else:
                    valid_tiles = set()
                    for option in self.grid[y][x].options:
                        # Set union operator — accumulate all tiles reachable in this direction.
                        valid_tiles |= self.neighbors.get(option, {}).get(
                            direction, set()
                        )

                # Set intersection operator — eliminate options inconsistent with neighbors.
                self.grid[ny][nx].options &= valid_tiles
                self.grid[ny][nx].propagated = True
                self.grid[ny][nx].compute_superposition_tile(
                    tile_weights=self.tile_weights,
                    color_mapping=self.color_mapping,
                )

                self.propagate(ny, nx, recursion_depth - 1)

        for y in range(self.grid_dimensions.height):
            for x in range(self.grid_dimensions.width):
                self.grid[y][x].propagated = False

    def _collapse_grid_cell(self, y: int, x: int, tile: Tile) -> None:
        """
        Collapse the grid cell at (y, x) to a single tile.

        Args:
            y (int): The row index of the cell to collapse.
            x (int): The column index of the cell to collapse.
            tile (Tile): The tile to collapse the cell to.
        """
        self.grid[y][x].options = set()
        self.grid[y][x].collapsed = True
        self.grid[y][x].tile = tile
        self.grid[y][x].superposition_tile = None

    def collapse_grid(self) -> None:
        """
        Run the WFC algorithm until all grid cells are collapsed.

        Iteratively selects the uncollapsed cell with the fewest remaining tile
        options (lowest entropy), collapses it to a weighted random tile, and
        propagates the resulting constraints to its neighbors.

        1. Find all uncollapsed cells with the minimum number of remaining options.
        2. If no uncollapsed cells remain, pause briefly and exit.
        3. Select one minimum-entropy cell at random.
        4. Collapse it to a tile chosen by weighted random selection.
        5. Propagate constraints outward from the collapsed cell.
        6. Render the current grid state via the visualizer.
        """
        while True:
            # Entropy pass — find all cells tied for the lowest number of options.
            min_entropy = float("inf")
            min_cells = []

            for cell_y in range(self.grid_dimensions.height):
                for cell_x in range(self.grid_dimensions.width):
                    if not self.grid[cell_y][cell_x].collapsed:
                        options = self.grid[cell_y][cell_x].options

                        if len(options) < min_entropy:
                            min_entropy = len(options)
                            min_cells = [(cell_y, cell_x)]
                        elif len(options) == min_entropy:
                            min_cells.append((cell_y, cell_x))

            if not min_cells:
                time.sleep(3)
                break

            # Collapse step — select and collapse a minimum-entropy cell.
            y, x = rd.choice(min_cells)
            choices = list(self.grid[y][x].options)
            weights = [self.tile_weights[tile] for tile in choices]
            chosen_tile = rd.choices(choices, weights)[0]
            self._collapse_grid_cell(y, x, chosen_tile)
            self.propagate(y, x, recursion_depth=self.recursion_depth)

            self.wfc_visualizer.visualize(self.grid)
