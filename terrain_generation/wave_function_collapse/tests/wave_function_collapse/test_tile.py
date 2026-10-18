"""Tests for the tile module."""

from wave_function_collapse.tile import Tile


# Testing the "__init__" method from the "Tile" class.


def test_init_computes_directional_slices() -> None:
    tile = Tile((("A", "B"), ("C", "D")))

    assert tile.up == (("A", "B"),)
    assert tile.down == (("C", "D"),)
    assert tile.left == (("A",), ("C",))
    assert tile.right == (("B",), ("D",))


# Testing the "__eq__" and "__hash__" methods from the "Tile" class.


def test_equal_patterns_are_the_same_tile() -> None:
    first = Tile((("A", "B"), ("C", "D")))
    second = Tile((("A", "B"), ("C", "D")))

    assert first == second
    assert hash(first) == hash(second)
    assert len({first, second}) == 1


def test_tile_is_not_equal_to_other_objects() -> None:
    tile = Tile((("A",),))

    assert tile != "A"


# Testing the "__repr__" method from the "Tile" class.


def test_repr_shows_the_pattern() -> None:
    tile = Tile((("A", "B"), ("C", "D")))

    assert repr(tile) == str((("A", "B"), ("C", "D")))
