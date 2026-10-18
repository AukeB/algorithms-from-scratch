"""Tests for the renderer module."""

import logging

import pygame as pg
import pytest

from voronoi_diagram.config_model import ConfigModel
from voronoi_diagram.constants import Position
from voronoi_diagram.grid import Grid
from voronoi_diagram.renderer import Renderer


def _has_drawn_pixels(surface: pg.Surface) -> bool:
    """Report whether anything other than black has been drawn on a surface.

    Args:
        surface (pg.Surface): The surface to inspect, which starts out black.

    Returns:
        drawn (bool): True if any pixel has a non-zero color channel.
    """
    average = pg.transform.average_color(surface)
    drawn = any(channel > 0 for channel in average[:3])

    return drawn


@pytest.fixture(name="renderer")
def fixture_renderer(small_config: ConfigModel) -> Renderer:
    """Provide a renderer with a headless window.

    Args:
        small_config (ConfigModel): The validated configuration.

    Returns:
        renderer (Renderer): The renderer, ready to draw.
    """
    renderer = Renderer(config=small_config)

    return renderer


@pytest.fixture(name="grid")
def fixture_grid(small_config: ConfigModel, renderer: Renderer) -> Grid:
    """Provide a grid with a Voronoi diagram, matching the renderer.

    Args:
        small_config (ConfigModel): The validated configuration.
        renderer (Renderer): The renderer, to keep the grid size in step with.

    Returns:
        grid (Grid): The grid, ready to draw.
    """
    grid = Grid(config=small_config)
    grid.seed_points = [Position(x=2.5, y=2.5), Position(x=7.5, y=7.5)]
    grid.generate_voronoi_diagram()

    return grid


# Testing the "__init__" method from the "Renderer" class.


def test_init_snaps_cell_size_to_whole_pixels(renderer: Renderer) -> None:
    assert isinstance(renderer.cell_size, int)
    assert renderer.grid_size == renderer.cell_size * 10


def test_init_creates_one_color_per_seed(renderer: Renderer) -> None:
    assert len(renderer.seed_point_colors) == 4
    assert len(renderer.voronoi_cell_colors) == 4


# Testing the "_snap_to_pixel_grid" method from the "Renderer" class.


def test_snap_to_pixel_grid_logs_the_adjustment(
    renderer: Renderer, caplog: pytest.LogCaptureFixture
) -> None:
    renderer.cell_size = 10.4
    renderer.grid_size = 104.0
    renderer.screen_size = renderer.screen_size.__class__(width=1000, height=800)

    with caplog.at_level(logging.INFO, logger="voronoi_diagram.renderer"):
        renderer._snap_to_pixel_grid()

    assert renderer.cell_size == 10
    assert renderer.grid_size == 100
    assert "Cell-size snapping" in caplog.text


# Testing the "tick" method from the "Renderer" class.


def test_tick_waits_without_error(renderer: Renderer) -> None:
    renderer.tick(fps=1000)


# Testing the "_draw_grid_lines" method from the "Renderer" class.


def test_draw_grid_lines_draws_on_the_screen(renderer: Renderer) -> None:
    renderer.screen.fill((0, 0, 0))

    renderer._draw_grid_lines()

    assert _has_drawn_pixels(renderer.screen)


# Testing the "_draw_cells" method from the "Renderer" class.


def test_draw_cells_fills_each_region_with_its_color(
    renderer: Renderer, grid: Grid
) -> None:
    renderer.screen.fill((0, 0, 0))

    renderer._draw_cells(grid=grid)

    first_cell_pixel = renderer.screen.get_at(
        (renderer.margin_size, renderer.margin_size)
    )
    assert tuple(first_cell_pixel)[:3] == renderer.voronoi_cell_colors[grid.cells[0][0]]


# Testing the "_draw_seed_points" method from the "Renderer" class.


def test_draw_seed_points_paints_each_marker_center(renderer: Renderer, grid: Grid) -> None:
    renderer.screen.fill((0, 0, 0))

    renderer._draw_seed_points(grid=grid)

    seed = grid.seed_points[0]
    center = (
        int(renderer.margin_size + seed.x * renderer.cell_size),
        int(renderer.margin_size + seed.y * renderer.cell_size),
    )
    assert tuple(renderer.screen.get_at(center))[:3] == renderer.seed_point_colors[0]


# Testing the "render" method from the "Renderer" class.


@pytest.mark.parametrize("show_gridlines", [False, True])
def test_render_draws_a_frame(
    renderer: Renderer, grid: Grid, show_gridlines: bool
) -> None:
    renderer.show_gridlines = show_gridlines

    renderer.render(grid=grid)

    assert _has_drawn_pixels(renderer.screen)


# Testing the "quit" method from the "Renderer" class.


def test_quit_shuts_pygame_down(renderer: Renderer) -> None:
    renderer.quit()

    assert not pg.display.get_init()
