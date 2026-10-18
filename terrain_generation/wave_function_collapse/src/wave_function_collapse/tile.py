"""Module for the Tile data structure used by the Wave Function Collapse algorithm."""

from wave_function_collapse.constants import TileValue


class Tile:
    """A square pattern of characters, and the edge slices used to match it with
    neighbors.

    Two tiles are equal when their values are equal, so identical patterns from
    different places in the bitmap count as the same tile.

    Attributes:
        value (TileValue): The pattern, as rows of characters.
        up (TileValue): The pattern without its last row, which must match the neighbor
            above.
        down (TileValue): The pattern without its first row, which must match the
            neighbor below.
        left (TileValue): The pattern without its last column, which must match the
            neighbor to the left.
        right (TileValue): The pattern without its first column, which must match the
            neighbor to the right.

    Example:
        >>> tile = Tile((("A", "B"), ("C", "D")))
        >>> tile.up
        (('A', 'B'),)
    """

    def __init__(self, tile: TileValue) -> None:
        """Store the pattern and compute its edge slices.

        Args:
            tile (TileValue): The pattern, as rows of characters.
        """
        self.value = tile

        self.up = tile[:-1]
        self.down = tile[1:]
        self.right = tuple(row[1:] for row in tile)
        self.left = tuple(row[:-1] for row in tile)

    def __repr__(self) -> str:
        """Return the pattern as text.

        Returns:
            value_str (str): The string form of the pattern.
        """
        value_str = str(self.value)

        return value_str

    def __hash__(self) -> int:
        """Hash the pattern, so tiles can be used in sets and as dict keys.

        Returns:
            tile_hash (int): The hash of the pattern.
        """
        tile_hash = hash(self.value)

        return tile_hash

    def __eq__(self, other: object) -> bool:
        """Check whether another object is a tile with the same pattern.

        Args:
            other (object): The object to compare against.

        Returns:
            are_equal (bool): True if other is a Tile with an identical pattern.
        """
        are_equal = isinstance(other, Tile) and self.value == other.value

        return are_equal
