"""Tests for the utils_colors module."""

from voronoi_diagram.utils.utils_colors import generate_voronoi_colors


# Testing the "generate_voronoi_colors" function.


def test_generate_voronoi_colors_returns_one_color_per_seed() -> None:
    seed_colors, cell_colors = generate_voronoi_colors(num_seeds=5)

    assert len(seed_colors) == 5
    assert len(cell_colors) == 5


def test_seed_colors_are_darker_than_cell_colors() -> None:
    seed_colors, cell_colors = generate_voronoi_colors(num_seeds=3)

    for seed_color, cell_color in zip(seed_colors, cell_colors):
        assert sum(seed_color) < sum(cell_color)


def test_colors_are_valid_rgb_triples() -> None:
    seed_colors, cell_colors = generate_voronoi_colors(num_seeds=7)

    for color in seed_colors + cell_colors:
        assert len(color) == 3
        assert all(0 <= channel <= 255 for channel in color)
