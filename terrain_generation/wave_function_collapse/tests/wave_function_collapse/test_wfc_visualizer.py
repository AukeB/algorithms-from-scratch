"""Tests for the wfc_visualizer module."""

import pygame as pg
import pytest

from wave_function_collapse.config_model import ConfigModel
from wave_function_collapse.grid_cell import GridCell
from wave_function_collapse.tile import Tile
from wave_function_collapse.wfc_visualizer import WFCVisualizer

_COLOR_MAPPING = {(255, 0, 0): "A", (0, 0, 255): "B"}


@pytest.fixture(name="visualizer")
def fixture_visualizer(small_config: ConfigModel) -> WFCVisualizer:
    """Provide a visualizer with a headless window.

    Args:
        small_config (ConfigModel): The small test configuration.

    Returns:
        visualizer (WFCVisualizer): The visualizer, ready to draw.
    """
    visualizer = WFCVisualizer(config=small_config, color_mapping=_COLOR_MAPPING)

    return visualizer


def _open_cell(show_superposition: bool = False) -> GridCell:
    """Create an uncollapsed cell.

    Args:
        show_superposition (bool): Whether the cell computes its superposition colour.

    Returns:
        cell (GridCell): The open cell.
    """
    red_tile = Tile((("A", "A"), ("A", "A")))
    cell = GridCell(
        tile_set={red_tile},
        tile_weights={red_tile: 1.0},
        inverted_color_mapping={"A": (255, 0, 0), "B": (0, 0, 255)},
        show_superposition=show_superposition,
    )

    return cell


# Testing the "__init__" method from the "WFCVisualizer" class.


def test_init_sizes_the_squares_to_fit_the_window(visualizer: WFCVisualizer) -> None:
    expected = int((visualizer.screen_size.height - 40) / 6)

    assert visualizer.tile_size_px == expected


# Testing the "_compute_tile_position" method from the "WFCVisualizer" class.


def test_compute_tile_position_offsets_by_margin(visualizer: WFCVisualizer) -> None:
    y, x = visualizer._compute_tile_position(row_index=1, col_index=2)

    assert y == 20 + visualizer.tile_size_px
    assert x == 20 + 2 * visualizer.tile_size_px


# Testing the "_cell_color" method from the "WFCVisualizer" class.


def test_cell_color_uses_the_centre_of_a_collapsed_tile(visualizer: WFCVisualizer) -> None:
    cell = _open_cell()
    cell.collapsed = True
    cell.tile = Tile((("A", "B"), ("B", "B")))

    assert visualizer._cell_color(cell=cell) == (0, 0, 255)


def test_cell_color_uses_superposition_when_shown(visualizer: WFCVisualizer) -> None:
    visualizer.show_superposition = True
    cell = _open_cell(show_superposition=True)

    color = visualizer._cell_color(cell=cell)

    assert color == (255, 0, 0)


def test_cell_color_falls_back_to_background(visualizer: WFCVisualizer) -> None:
    visualizer.show_superposition = False
    cell = _open_cell(show_superposition=True)

    assert visualizer._cell_color(cell=cell) == visualizer.grid_background_color


# Testing the "_draw_tile" method from the "WFCVisualizer" class.


def test_draw_tile_paints_the_square(visualizer: WFCVisualizer) -> None:
    visualizer.screen.fill((0, 0, 0))
    cell = _open_cell()
    cell.collapsed = True
    cell.tile = Tile((("B", "B"), ("B", "B")))

    visualizer._draw_tile(cell=cell, y=20, x=20)

    assert tuple(visualizer.screen.get_at((25, 25)))[:3] == (0, 0, 255)


# Testing the "visualize" method from the "WFCVisualizer" class.


def test_visualize_keeps_running_without_input(
    visualizer: WFCVisualizer, scripted_input: object
) -> None:
    grid = [[_open_cell() for _ in range(6)] for _ in range(6)]

    keep_running = visualizer.visualize(grid=grid)

    assert keep_running is True


def test_visualize_stops_when_the_window_is_closed(
    visualizer: WFCVisualizer, scripted_input: object
) -> None:
    grid = [[_open_cell() for _ in range(6)] for _ in range(6)]
    scripted_input([[pg.event.Event(pg.QUIT)]])

    keep_running = visualizer.visualize(grid=grid)

    assert keep_running is False


def test_visualize_stops_on_escape(
    visualizer: WFCVisualizer, scripted_input: object
) -> None:
    grid = [[_open_cell() for _ in range(6)] for _ in range(6)]
    scripted_input([[pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE)]])

    keep_running = visualizer.visualize(grid=grid)

    assert keep_running is False


# Testing the "quit" method from the "WFCVisualizer" class.


def test_quit_shuts_pygame_down(visualizer: WFCVisualizer) -> None:
    visualizer.quit()

    assert not pg.display.get_init()
