"""Tests for the grid module."""

from typing import Any

import pytest

from eca.config.config_model import ConfigModel
from eca.constants import Dimensions
from eca.errors import UnsupportedBoundaryModeError, UnsupportedInitializationModeError
from eca.grid import Grid


# Testing the "__init__" method from the "Grid" class.


def test_init_creates_empty_square_grid(config_data: dict[str, Any]) -> None:
    grid = Grid(config=ConfigModel(**config_data))

    assert grid.dimensions == Dimensions(rows=5, cols=5)
    assert grid.grid == [[0] * 5 for _ in range(5)]


# Testing the "_get_padded_row" method from the "Grid" class.


@pytest.mark.parametrize(
    ("boundary_mode", "expected"),
    [
        ("zero", [0, 1, 0, 0, 0]),
        ("periodic", [0, 1, 0, 0, 1]),
        ("reflective", [1, 1, 0, 0, 0]),
    ],
)
def test_get_padded_row_applies_boundary_mode(boundary_mode: str, expected: list[int]) -> None:
    padded_row = Grid._get_padded_row(row=[1, 0, 0], boundary_mode=boundary_mode)

    assert padded_row == expected


def test_get_padded_row_rejects_unknown_boundary_mode() -> None:
    with pytest.raises(UnsupportedBoundaryModeError):
        Grid._get_padded_row(row=[1, 0, 0], boundary_mode="unknown")


# Testing the "initialize" method from the "Grid" class.


def test_initialize_single_alive_cell(config_data: dict[str, Any]) -> None:
    grid = Grid(config=ConfigModel(**config_data))

    grid.initialize()

    assert grid.grid[0] == [0, 0, 1, 0, 0]


def test_initialize_single_dead_cell(config_data: dict[str, Any]) -> None:
    config_data["game"]["initialization_mode"] = "single_dead_cell"
    grid = Grid(config=ConfigModel(**config_data))

    grid.initialize()

    assert grid.grid[0] == [1, 1, 0, 1, 1]


def test_initialize_random_uses_only_binary_values(config_data: dict[str, Any]) -> None:
    config_data["game"]["initialization_mode"] = "random"
    grid = Grid(config=ConfigModel(**config_data))

    grid.initialize()

    assert len(grid.grid[0]) == 5
    assert set(grid.grid[0]) <= {0, 1}


def test_initialize_rejects_unknown_mode(config_data: dict[str, Any]) -> None:
    grid = Grid(config=ConfigModel(**config_data))
    grid._initialization_mode = "unknown"

    with pytest.raises(UnsupportedInitializationModeError):
        grid.initialize()


# Testing the "is_full" property from the "Grid" class.


def test_is_full_false_before_last_row(config_data: dict[str, Any]) -> None:
    grid = Grid(config=ConfigModel(**config_data))

    assert grid.is_full is False


def test_is_full_true_at_last_row(config_data: dict[str, Any]) -> None:
    grid = Grid(config=ConfigModel(**config_data))
    grid._iteration = grid.dimensions.rows - 1

    assert grid.is_full is True


# Testing the "propagate" method from the "Grid" class.


def test_propagate_applies_rule_90_with_zero_boundary(config_data: dict[str, Any]) -> None:
    grid = Grid(config=ConfigModel(**config_data))
    grid.initialize()

    grid.propagate()

    assert grid.grid[1] == [0, 1, 0, 1, 0]


def test_propagate_stores_each_row_at_next_iteration(config_data: dict[str, Any]) -> None:
    grid = Grid(config=ConfigModel(**config_data))
    grid.initialize()

    grid.propagate()
    grid.propagate()

    assert grid.grid[2] == [1, 0, 0, 0, 1]
