"""Module for the Tile data structure used in the WFC algorithm."""

from src.wave_function_collapse.constants import TileValue


class Tile:
    """
    Represents a square tile and its directional overlap slices.

    A tile is a 2D grid of characters derived from the input bitmap. For each
    direction, a slice of the tile is stored that represents the overlap region
    used by the WFC algorithm to determine which tiles can be placed adjacent
    to one another.
    """

    def __init__(
        self,
        tile: TileValue,
    ) -> None:
        """
        Store the tile value and pre-compute its directional overlap slices.

        Args:
            tile (TileValue): A 2D tuple of characters representing the tile.
        """
        self.value = tile

        # Each directional slice drops one row or column from the tile, leaving
        # the overlap region that must match the neighbor in that direction.
        self.up = tile[:-1]
        self.down = tile[1:]
        self.right = tuple(row[1:] for row in tile)
        self.left = tuple(row[:-1] for row in tile)

    def __repr__(self) -> str:
        """
        Return a string representation of the tile value.

        Called by repr() and used by debuggers and REPLs. Also serves as the
        fallback for print() since this class does not define __str__.

        Returns:
            value_str (str): The string representation of the tile value.
        """
        value_str = str(self.value)

        return value_str

    def __hash__(self) -> int:
        """
        Return a hash of the tile value.

        A hash is a fixed-size integer fingerprint derived from the tile's value.
        Python uses it as a fast lookup key in dicts and sets — rather than comparing
        objects directly, it first compares hashes, which is far cheaper. Two tiles
        that are equal must always produce the same hash, which is why __hash__ and
        __eq__ are always defined together.

        Returns:
            tile_hash (int): The hash of the tile's value tuple.
        """
        tile_hash = hash(self.value)

        return tile_hash

    def __eq__(self, other: object) -> bool:
        """
        Check equality between this tile and another object.

        Two tiles are considered equal if they are both Tile instances and their
        values are identical. This ensures that structurally identical tiles
        extracted from different positions in the bitmap are treated as the same tile.

        Args:
            other (object): The object to compare against.

        Returns:
            are_equal (bool): True if other is a Tile with an identical value, False otherwise.
        """
        are_equal = isinstance(other, Tile) and self.value == other.value

        return are_equal
