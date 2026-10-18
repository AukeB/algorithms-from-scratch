"""Tests for the grid module."""

import random

from voronoi_diagram.config_model import ConfigModel
from voronoi_diagram.constants import Position
from voronoi_diagram.grid import Grid


# Testing the "__init__" method from the "Grid" class.


def test_init_creates_empty_square_grid(small_config: ConfigModel) -> None:
    grid = Grid(config=small_config)

    assert tuple(grid.dimensions) == (10, 10)
    assert grid.cells == [[0] * 10 for _ in range(10)]
    assert grid.seed_points == []


# Testing the "generate_seed_points" method from the "Grid" class.


def test_generate_seed_points_places_points_at_cell_centers(
    small_config: ConfigModel,
) -> None:
    grid = Grid(config=small_config, rng=random.Random(1))

    grid.generate_seed_points(num_seeds=6)

    assert len(grid.seed_points) == 6
    for seed in grid.seed_points:
        assert seed.x % 1 == 0.5
        assert seed.y % 1 == 0.5
        assert 0 < seed.x < 10
        assert 0 < seed.y < 10


# Testing the "_find_closest_seed" method from the "Grid" class.


def test_find_closest_seed_returns_nearest_index(small_config: ConfigModel) -> None:
    grid = Grid(config=small_config)
    grid.seed_points = [Position(x=0.5, y=0.5), Position(x=9.5, y=9.5)]

    assert grid._find_closest_seed(Position(x=1.0, y=1.0)) == 0
    assert grid._find_closest_seed(Position(x=8.0, y=9.0)) == 1


# Testing the "generate_voronoi_diagram" method from the "Grid" class.


def test_generate_voronoi_diagram_assigns_cells_to_nearest_seed(
    small_config: ConfigModel,
) -> None:
    grid = Grid(config=small_config)
    grid.seed_points = [Position(x=0.5, y=0.5), Position(x=9.5, y=9.5)]

    grid.generate_voronoi_diagram()

    assert grid.cells[0][0] == 0
    assert grid.cells[9][9] == 1
    assert grid.cells[0][9] == 0 or grid.cells[0][9] == 1
