"""Tests for the grid_cell module."""

from wave_function_collapse.grid_cell import GridCell
from wave_function_collapse.tile import Tile

_RED_TILE = Tile((("A", "A"), ("A", "A")))
_BLUE_TILE = Tile((("B", "B"), ("B", "B")))
_INVERTED = {"A": (255, 0, 0), "B": (0, 0, 255)}


# Testing the "__init__" method from the "GridCell" class.


def test_init_starts_open_with_all_tiles() -> None:
    cell = GridCell(
        tile_set={_RED_TILE, _BLUE_TILE},
        tile_weights={_RED_TILE: 0.5, _BLUE_TILE: 0.5},
        inverted_color_mapping=_INVERTED,
        show_superposition=False,
    )

    assert cell.options == {_RED_TILE, _BLUE_TILE}
    assert cell.collapsed is False
    assert cell.tile is None
    assert cell.superposition_tile is None


# Testing the "compute_superposition_tile" method from the "GridCell" class.


def test_superposition_is_the_weighted_average_colour() -> None:
    cell = GridCell(
        tile_set={_RED_TILE, _BLUE_TILE},
        tile_weights={_RED_TILE: 0.75, _BLUE_TILE: 0.25},
        inverted_color_mapping=_INVERTED,
        show_superposition=True,
    )

    assert cell.superposition_tile is not None
    assert cell.superposition_tile[0][0] == (191, 0, 63)


def test_superposition_is_skipped_when_not_shown() -> None:
    cell = GridCell(
        tile_set={_RED_TILE},
        tile_weights={_RED_TILE: 1.0},
        inverted_color_mapping=_INVERTED,
        show_superposition=False,
    )

    cell.compute_superposition_tile(
        tile_weights={_RED_TILE: 1.0},
        inverted_color_mapping=_INVERTED,
        show_superposition=False,
    )

    assert cell.superposition_tile is None


def test_superposition_is_cleared_when_no_options_are_left() -> None:
    cell = GridCell(
        tile_set={_RED_TILE},
        tile_weights={_RED_TILE: 1.0},
        inverted_color_mapping=_INVERTED,
        show_superposition=True,
    )
    cell.options = set()

    cell.compute_superposition_tile(
        tile_weights={_RED_TILE: 1.0},
        inverted_color_mapping=_INVERTED,
        show_superposition=True,
    )

    assert cell.superposition_tile is None


# Testing the "__repr__" method from the "GridCell" class.


def test_repr_shows_collapsed_state() -> None:
    cell = GridCell(
        tile_set={_RED_TILE},
        tile_weights={_RED_TILE: 1.0},
        inverted_color_mapping=_INVERTED,
        show_superposition=False,
    )

    assert repr(cell) == "False"
