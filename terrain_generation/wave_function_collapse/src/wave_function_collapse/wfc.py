"""Module for the Wave Function Collapse algorithm."""

import random
from collections import Counter, defaultdict

from wave_function_collapse.config_model import ConfigModel
from wave_function_collapse.constants import DIRECTIONS, Dimensions, RGBColor
from wave_function_collapse.errors import ContradictionError
from wave_function_collapse.grid_cell import GridCell
from wave_function_collapse.tile import Tile
from wave_function_collapse.wfc_visualizer import WFCVisualizer


class WaveFunctionCollapse:
    """Fill a grid with tiles that look locally like the input bitmap.

    The tiles and their frequencies come from the bitmap. Each step collapses the
    uncollapsed cell with the fewest options to one tile, chosen at random by frequency,
    and then propagates the consequences to its neighbors.

    Attributes:
        bitmap (list[list[str]]): The bitmap as rows of characters.
        bitmap_dimensions (Dimensions): Number of rows and columns of the bitmap.
        grid_dimensions (Dimensions): Number of rows and columns of the output grid.
        tile_dimensions (Dimensions): Number of rows and columns of each tile.
        recursion_depth (int): How many cells outward constraints propagate per
            collapse.
        show_superposition (bool): Whether uncollapsed cells compute their average
            colour.
        color_mapping (dict[RGBColor, str]): Maps each colour to its character.
        inverted_color_mapping (dict[str, RGBColor]): Maps each character to its colour.
        directions (dict[str, tuple[int, int]]): Offsets to the neighbor in each
            direction.
        rng (random.Random): Random generator for the choices made during collapse.
        visualizer (WFCVisualizer | None): Draws each step, or None to run without
            drawing.
        tile_weights (dict[Tile, float]): The frequency weight of each unique tile.
        all_tiles (list[Tile]): Every tile extracted from the bitmap, duplicates
            included.
        tile_set (set[Tile]): The unique tiles.
        neighbors (defaultdict): For each tile and direction, the tiles allowed there.
        grid (list[list[GridCell]]): The output grid.

    Example:
        >>> wfc = WaveFunctionCollapse(config=config, bitmap=mapped_bitmap, color_mapping=mapping)
        >>> wfc.collapse_grid()
    """

    def __init__(
        self,
        config: ConfigModel,
        bitmap: list[list[str]],
        color_mapping: dict[RGBColor, str],
        visualizer: WFCVisualizer | None = None,
        rng: random.Random | None = None,
    ) -> None:
        """Extract the tiles from the bitmap, and start with every cell open.

        Args:
            config (ConfigModel): The validated configuration model.
            bitmap (list[list[str]]): The bitmap as rows of characters.
            color_mapping (dict[RGBColor, str]): Maps each colour to its character.
            visualizer (WFCVisualizer | None): Draws each step. None runs without
                drawing.
            rng (random.Random | None): Random generator for the collapse choices.
                Defaults to a new, unseeded generator.

        Raises:
            NotImplementedError: If the configured model or boundary mode is not
                implemented.
        """
        self._validate_modes(config=config)

        self.bitmap = bitmap
        self.bitmap_dimensions = Dimensions(rows=len(bitmap), cols=len(bitmap[0]))
        self.grid_dimensions = Dimensions(
            rows=config.general.grid_dim,
            cols=config.general.grid_dim,
        )
        self.tile_dimensions = Dimensions(
            rows=config.general.tile_dim,
            cols=config.general.tile_dim,
        )
        self.recursion_depth = config.general.recursion_depth
        self.show_superposition = config.general.show_superposition
        self.color_mapping = color_mapping
        self.inverted_color_mapping = {
            character: color for color, character in color_mapping.items()
        }
        self.directions = DIRECTIONS
        self.rng = rng if rng is not None else random.Random()
        self.visualizer = visualizer

        self._flagged_cells: set[tuple[int, int]] = set()

        self._validate_tile_and_bitmap_dimensions()
        self.tile_weights, self.all_tiles = self._compute_tiles_and_weights()
        self.tile_set = set(self.tile_weights.keys())
        self.neighbors = self._compute_neighbors()
        self.grid = self._initialize_grid()

    def _validate_modes(self, config: ConfigModel) -> None:
        """Check that the configured model and boundary mode are implemented.

        Args:
            config (ConfigModel): The validated configuration model.

        Raises:
            NotImplementedError: If the model is not "overlapping", or the boundary mode
                is not "wrap_around".
        """
        if config.modes.mode_model != "overlapping":
            raise NotImplementedError(
                f"mode_model '{config.modes.mode_model}' is not implemented yet."
            )

        if config.modes.mode_boundary_conditions != "wrap_around":
            raise NotImplementedError(
                f"mode_boundary_conditions '{config.modes.mode_boundary_conditions}' is not "
                "implemented yet."
            )

    def _validate_tile_and_bitmap_dimensions(self) -> None:
        """Check that a tile fits inside the bitmap.

        Raises:
            ValueError: If a tile dimension is larger than the smallest bitmap
                dimension.
        """
        smallest_bitmap_dim = min(
            self.bitmap_dimensions.rows, self.bitmap_dimensions.cols
        )

        if (
            self.tile_dimensions.rows > smallest_bitmap_dim
            or self.tile_dimensions.cols > smallest_bitmap_dim
        ):
            raise ValueError(
                f"tile_dim ({self.tile_dimensions.rows}) must be no larger than the smallest "
                f"bitmap dimension (rows: {self.bitmap_dimensions.rows}, "
                f"cols: {self.bitmap_dimensions.cols})."
            )

    def _extract_tile(self, x: int, y: int) -> Tile:
        """Extract the tile whose top-left corner is at (x, y). The bitmap wraps around
        its edges.

        Args:
            x (int): Column of the top-left corner.
            y (int): Row of the top-left corner.

        Returns:
            tile (Tile): The extracted tile.
        """
        tile_rows: list[tuple[str, ...]] = []

        for row_offset in range(self.tile_dimensions.rows):
            source_row = self.bitmap[(y + row_offset) % self.bitmap_dimensions.rows]
            tile_row: list[str] = []

            for col_offset in range(self.tile_dimensions.cols):
                source_col = (x + col_offset) % self.bitmap_dimensions.cols
                tile_row.append(source_row[source_col])

            tile_rows.append(tuple(tile_row))

        tile_value = tuple(tile_rows)
        tile = Tile(tile_value)

        return tile

    def _compute_tiles_and_weights(self) -> tuple[dict[Tile, float], list[Tile]]:
        """Extract a tile at every bitmap position, and weight each unique tile by its
        frequency.

        Returns:
            result (tuple[dict[Tile, float], list[Tile]]): The weight of each unique
                tile, which sum to 1, and every extracted tile in order.
        """
        tile_count: Counter[Tile] = Counter()
        all_tiles: list[Tile] = []
        total_positions = self.bitmap_dimensions.rows * self.bitmap_dimensions.cols

        for y in range(self.bitmap_dimensions.rows):
            for x in range(self.bitmap_dimensions.cols):
                tile = self._extract_tile(x=x, y=y)
                tile_count[tile] += 1
                all_tiles.append(tile)

        tile_weights = {
            tile: count / total_positions for tile, count in tile_count.items()
        }

        return tile_weights, all_tiles

    def _compute_neighbors(self) -> defaultdict:
        """Find, for each tile and direction, which tiles may sit in that direction.

        Two tiles fit when the overlapping edges of their patterns are identical. For
        example, a tile may sit above another when the other's top rows match this
        tile's bottom rows.

        Returns:
            neighbors (defaultdict): Maps each tile to a dict of directions, each
                holding the set of tiles that may sit in that direction.
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
        """Create every grid cell, with all tiles as its options.

        Returns:
            grid (list[list[GridCell]]): The output grid.
        """
        grid: list[list[GridCell]] = []

        for _ in range(self.grid_dimensions.rows):
            grid_row: list[GridCell] = []

            for _ in range(self.grid_dimensions.cols):
                cell = GridCell(
                    tile_set=self.tile_set.copy(),
                    tile_weights=self.tile_weights,
                    inverted_color_mapping=self.inverted_color_mapping,
                    show_superposition=self.show_superposition,
                )
                grid_row.append(cell)

            grid.append(grid_row)

        return grid

    def _valid_tiles_towards(self, y: int, x: int, direction: str) -> set[Tile]:
        """Find the tiles that a cell allows in one direction.

        A collapsed cell allows the tiles that fit its tile. An open cell allows the
        union over all its options.

        Args:
            y (int): Row of the source cell.
            x (int): Column of the source cell.
            direction (str): The direction to look in.

        Returns:
            valid_tiles (set[Tile]): The tiles allowed in that direction.
        """
        source_cell = self.grid[y][x]

        if source_cell.tile is not None:
            valid_tiles = self.neighbors.get(source_cell.tile, {}).get(direction, set())
            return valid_tiles

        valid_tiles = set()
        for option in source_cell.options:
            valid_tiles |= self.neighbors.get(option, {}).get(direction, set())

        return valid_tiles

    def _clear_propagated_flags(self) -> None:
        """Clear the propagated flag of every cell that was flagged during propagation."""
        for cell_y, cell_x in self._flagged_cells:
            self.grid[cell_y][cell_x].propagated = False

        self._flagged_cells.clear()

    def propagate(self, y: int, x: int, recursion_depth: int) -> None:
        """Narrow the options of the open cells around (y, x), and keep going outward.

        For each open neighbor, its options are intersected with the tiles that the
        source allows in that direction. Each neighbor that changed is then propagated
        from in turn, up to recursion_depth steps.

        Args:
            y (int): Row of the source cell.
            x (int): Column of the source cell.
            recursion_depth (int): How many more steps outward to go.
        """
        if recursion_depth <= 0:
            return

        for direction, (dy, dx) in self.directions.items():
            neighbor_y = y + dy
            neighbor_x = x + dx

            if not (
                0 <= neighbor_x < self.grid_dimensions.cols
                and 0 <= neighbor_y < self.grid_dimensions.rows
            ):
                continue

            neighbor = self.grid[neighbor_y][neighbor_x]
            if neighbor.collapsed or neighbor.propagated:
                continue

            valid_tiles = self._valid_tiles_towards(y=y, x=x, direction=direction)
            neighbor.options &= valid_tiles
            neighbor.propagated = True
            self._flagged_cells.add((neighbor_y, neighbor_x))
            neighbor.compute_superposition_tile(
                tile_weights=self.tile_weights,
                inverted_color_mapping=self.inverted_color_mapping,
                show_superposition=self.show_superposition,
            )

            self.propagate(neighbor_y, neighbor_x, recursion_depth - 1)

        self._clear_propagated_flags()

    def _find_min_entropy_cells(self) -> list[tuple[int, int]]:
        """Find the uncollapsed cells with the fewest options.

        Returns:
            min_cells (list[tuple[int, int]]): The (row, column) of each uncollapsed
                cell that ties for the fewest options. Empty once every cell has
                collapsed.
        """
        min_entropy: int | None = None
        min_cells: list[tuple[int, int]] = []

        for cell_y in range(self.grid_dimensions.rows):
            for cell_x in range(self.grid_dimensions.cols):
                cell = self.grid[cell_y][cell_x]
                if cell.collapsed:
                    continue

                entropy = len(cell.options)
                if min_entropy is None or entropy < min_entropy:
                    min_entropy = entropy
                    min_cells = [(cell_y, cell_x)]
                elif entropy == min_entropy:
                    min_cells.append((cell_y, cell_x))

        return min_cells

    def _collapse_grid_cell(self, y: int, x: int) -> None:
        """Collapse one cell to a tile, chosen at random by frequency.

        Args:
            y (int): Row of the cell.
            x (int): Column of the cell.

        Raises:
            ContradictionError: If the cell has no options left.
        """
        cell = self.grid[y][x]
        options = list(cell.options)

        if not options:
            raise ContradictionError(row=y, col=x)

        weights = [self.tile_weights[tile] for tile in options]
        chosen_tile = self.rng.choices(options, weights=weights, k=1)[0]

        cell.options = set()
        cell.collapsed = True
        cell.tile = chosen_tile
        cell.superposition_tile = None

    def _draw_step(self) -> bool:
        """Draw the current grid, if there is a visualizer.

        Returns:
            keep_running (bool): False if the user asked to stop. True otherwise.
        """
        if self.visualizer is None:
            return True

        keep_running = self.visualizer.visualize(self.grid)

        return keep_running

    def collapse_grid(self) -> None:
        """Collapse every cell, one step at a time, until the grid is complete or the
        user stops.

        Raises:
            ContradictionError: If a cell is left with no tile that fits its neighbors.
        """
        keep_running = True

        while keep_running:
            candidates = self._find_min_entropy_cells()
            if not candidates:
                break

            y, x = self.rng.choice(candidates)
            self._collapse_grid_cell(y=y, x=x)
            self.propagate(y=y, x=x, recursion_depth=self.recursion_depth)

            keep_running = self._draw_step()
