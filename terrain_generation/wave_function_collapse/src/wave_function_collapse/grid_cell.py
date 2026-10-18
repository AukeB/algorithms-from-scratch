"""Module for the GridCell data structure used by the Wave Function Collapse algorithm."""

from wave_function_collapse.constants import RGBColor
from wave_function_collapse.tile import Tile


class GridCell:
    """One cell of the output grid. It holds the tiles it may still become, until it
    collapses.

    Attributes:
        options (set[Tile]): The tiles this cell can still collapse to.
        collapsed (bool): Whether the cell has collapsed to a single tile.
        tile (Tile | None): The tile the cell collapsed to, or None before that.
        superposition_tile (list[list[RGBColor]] | None): The weighted average colour of
            the remaining options, for display before collapse. None when it is not
            shown.
        propagated (bool): Whether this cell was reached by the current propagation
            pass.
    """

    def __init__(
        self,
        tile_set: set[Tile],
        tile_weights: dict[Tile, float],
        inverted_color_mapping: dict[str, RGBColor],
        show_superposition: bool,
    ) -> None:
        """Start with every tile as an option, and compute the superposition colour.

        Args:
            tile_set (set[Tile]): All tiles the cell can start with.
            tile_weights (dict[Tile, float]): The frequency weight of each tile.
            inverted_color_mapping (dict[str, RGBColor]): Maps each character to its
                colour.
            show_superposition (bool): Whether to compute the superposition colour.
        """
        self.options: set[Tile] = tile_set
        self.collapsed: bool = False
        self.tile: Tile | None = None
        self.superposition_tile: list[list[RGBColor]] | None = None
        self.propagated: bool = False

        self.compute_superposition_tile(
            tile_weights=tile_weights,
            inverted_color_mapping=inverted_color_mapping,
            show_superposition=show_superposition,
        )

    def __repr__(self) -> str:
        """Return whether the cell has collapsed.

        Returns:
            collapsed_str (str): The string form of the collapsed flag.
        """
        collapsed_str = str(self.collapsed)

        return collapsed_str

    def compute_superposition_tile(
        self,
        tile_weights: dict[Tile, float],
        inverted_color_mapping: dict[str, RGBColor],
        show_superposition: bool,
    ) -> None:
        """Compute the weighted average colour of the remaining options, pixel by pixel.

        Args:
            tile_weights (dict[Tile, float]): The frequency weight of each tile.
            inverted_color_mapping (dict[str, RGBColor]): Maps each character to its
                colour.
            show_superposition (bool): If False, nothing is computed.
        """
        if not show_superposition:
            return

        if not self.options:
            self.superposition_tile = None
            return

        sample_tile = next(iter(self.options))
        tile_rows = len(sample_tile.value)
        tile_cols = len(sample_tile.value[0])

        weighted_sums = [
            [[0.0, 0.0, 0.0] for _ in range(tile_cols)] for _ in range(tile_rows)
        ]
        total_weight = 0.0

        for tile in self.options:
            weight = tile_weights[tile]
            total_weight += weight

            for row_index, tile_row in enumerate(tile.value):
                for col_index, tile_cell in enumerate(tile_row):
                    red, green, blue = inverted_color_mapping[tile_cell]
                    sums = weighted_sums[row_index][col_index]
                    sums[0] += red * weight
                    sums[1] += green * weight
                    sums[2] += blue * weight

        rgb_matrix: list[list[RGBColor]] = []
        for sums_row in weighted_sums:
            rgb_row: list[RGBColor] = []

            for red_sum, green_sum, blue_sum in sums_row:
                red = int(red_sum / total_weight)
                green = int(green_sum / total_weight)
                blue = int(blue_sum / total_weight)
                rgb_row.append((red, green, blue))

            rgb_matrix.append(rgb_row)

        self.superposition_tile = rgb_matrix
