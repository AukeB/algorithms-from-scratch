"""Module for the GridCell data structure used in the WFC algorithm."""

from src.wave_function_collapse.tile import Tile
from src.wave_function_collapse.constants import RGBColor


class GridCell:
    """
    Represents a single cell in the WFC grid.

    Each cell starts in a superposition of all possible tiles and progressively
    collapses to a single tile as the WFC algorithm propagates constraints from
    neighboring cells. Before collapsing, the cell maintains a weighted average
    of all its possible tiles as a visual representation of its current state.

    Attributes:
        options (set[TileValue]): The set of tiles this cell can still collapse to.
        collapsed (bool): Whether the cell has been collapsed to a single tile.
        tile (TileValue | None): The tile this cell collapsed to, or None if not yet collapsed.
        superposition_tile (list[list[RGBColor]] | None): The weighted average RGB
            representation of all current tile options, or None before it is computed.
        propagated (bool): Whether this cell's constraints have been propagated to
            its neighbors in the current iteration.
    """

    def __init__(
        self,
        tile_set: set[Tile],
        tile_weights: dict[Tile, float],
        color_mapping: dict[RGBColor, str],
    ) -> None:
        """
        Initialise the cell with all tiles as options and compute its superposition tile.

        Args:
            tile_set (set[TileValue]): The set of all possible tiles this cell can collapse to.
            tile_weights (dict[TileValue, float]): A dict mapping each tile to its frequency weight.
            color_mapping (dict[RGBColor, str]): A dict mapping characters to RGB tuples.
        """
        self.options: set[Tile] = tile_set
        self.collapsed: bool = False
        self.tile: Tile | None = None
        self.superposition_tile: list[list[RGBColor]] | None = None
        self.propagated: bool = False

        self.compute_superposition_tile(
            tile_weights=tile_weights,
            color_mapping=color_mapping,
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the cell's collapsed state.

        Called by repr() and used by debuggers and REPLs. Also serves as the
        fallback for print() since this class does not define __str__.

        Returns:
            collapsed_str (str): The string representation of the collapsed flag.
        """
        collapsed_str = str(self.collapsed)

        return collapsed_str

    def compute_superposition_tile(
        self,
        tile_weights: dict[Tile, float],
        color_mapping: dict[RGBColor, str],
    ) -> None:
        """
        Compute a weighted average RGB tile across all current tile options.

        Each pixel in the resulting superposition tile is the weighted average
        of the corresponding pixel across all possible tiles, giving a visual
        impression of the cell's current state of uncertainty.

        1. Invert the color mapping so characters can be looked up by RGB value.
        2. Initialise an RGB matrix of zeros with the same dimensions as a tile.
        3. Accumulate the weighted RGB contribution of each possible tile.
        4. Divide each pixel by the total weight to produce the final average.
        5. Store the result in self.superposition_tile.

        Args:
            tile_weights (dict[Tile, float]): A dict mapping each tile
                to its frequency weight.
            color_mapping (dict[RGBColor, str]): A dict mapping RGB tuples
                to characters.
        """
        # Invert mapping so characters can be resolved back to RGB values.
        inverted_color_mapping = {v: k for k, v in color_mapping.items()}
        rgb_matrix: list[list[RGBColor]] = [
            [(0, 0, 0)] * len(row) for row in next(iter(self.options)).value
        ]

        # Accumulate weighted RGB contributions across all possible tiles.
        for tile in self.options:
            if tile in tile_weights:
                weight = tile_weights[tile]
                for row_index, tile_row in enumerate(tile.value):
                    for col_index, tile_cell in enumerate(tile_row):
                        r, g, b = inverted_color_mapping[tile_cell]
                        r_sum, g_sum, b_sum = rgb_matrix[row_index][col_index]
                        rgb_matrix[row_index][col_index] = (
                            int(r_sum + r * weight),
                            int(g_sum + g * weight),
                            int(b_sum + b * weight),
                        )

        # Normalise by total weight to produce the per-pixel average.
        total_weight = sum(
            tile_weights[tile] for tile in self.options if tile in tile_weights
        )
        for row_index in range(len(rgb_matrix)):
            for col_index in range(len(rgb_matrix[row_index])):
                r_sum, g_sum, b_sum = rgb_matrix[row_index][col_index]
                r_avg = int(r_sum / total_weight)
                g_avg = int(g_sum / total_weight)
                b_avg = int(b_sum / total_weight)
                rgb_matrix[row_index][col_index] = (r_avg, g_avg, b_avg)

        self.superposition_tile = rgb_matrix
