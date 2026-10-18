"""Tests for the wfc module."""

import random
from typing import Any

import pytest

from wave_function_collapse.config_model import ConfigModel
from wave_function_collapse.errors import ContradictionError
from wave_function_collapse.tile import Tile
from wave_function_collapse.wfc import WaveFunctionCollapse

_COLOR_MAPPING = {(255, 0, 0): "A", (0, 0, 255): "B"}


@pytest.fixture(name="wfc")
def fixture_wfc(small_config: ConfigModel, stripe_bitmap: list[list[str]]) -> WaveFunctionCollapse:
    """Provide the algorithm on the stripe bitmap, with a fixed seed.

    Args:
        small_config (ConfigModel): The small test configuration.
        stripe_bitmap (list[list[str]]): The stripe bitmap.

    Returns:
        wfc (WaveFunctionCollapse): The algorithm, ready to collapse.
    """
    wfc = WaveFunctionCollapse(
        config=small_config,
        bitmap=stripe_bitmap,
        color_mapping=_COLOR_MAPPING,
        rng=random.Random(0),
    )

    return wfc


# Testing the "__init__" method from the "WaveFunctionCollapse" class.


def test_init_uses_rows_and_columns_of_the_bitmap(wfc: WaveFunctionCollapse) -> None:
    assert tuple(wfc.bitmap_dimensions) == (4, 4)
    assert tuple(wfc.grid_dimensions) == (6, 6)
    assert tuple(wfc.tile_dimensions) == (2, 2)


def test_init_rejects_a_tile_larger_than_the_bitmap(
    small_config: ConfigModel, stripe_bitmap: list[list[str]]
) -> None:
    small_config.general.tile_dim = 5

    with pytest.raises(ValueError, match="must be no larger than"):
        WaveFunctionCollapse(config=small_config, bitmap=stripe_bitmap, color_mapping=_COLOR_MAPPING)


@pytest.mark.parametrize(
    ("mode_model", "mode_boundary_conditions", "message"),
    [
        ("simple-tiled", "wrap_around", "mode_model"),
        ("overlapping", "clamping", "mode_boundary_conditions"),
    ],
)
def test_init_rejects_unimplemented_modes(
    small_config: ConfigModel,
    stripe_bitmap: list[list[str]],
    mode_model: str,
    mode_boundary_conditions: str,
    message: str,
) -> None:
    small_config.modes.mode_model = mode_model  # type: ignore[assignment]
    small_config.modes.mode_boundary_conditions = mode_boundary_conditions  # type: ignore[assignment]

    with pytest.raises(NotImplementedError, match=message):
        WaveFunctionCollapse(config=small_config, bitmap=stripe_bitmap, color_mapping=_COLOR_MAPPING)


# Testing the "_extract_tile" method from the "WaveFunctionCollapse" class.


def test_extract_tile_wraps_around_the_bitmap_edges(wfc: WaveFunctionCollapse) -> None:
    tile = wfc._extract_tile(x=3, y=3)

    assert tile.value == (("A", "B"), ("B", "A"))


# Testing the "_compute_tiles_and_weights" method from the "WaveFunctionCollapse" class.


def test_weights_are_frequencies_that_sum_to_one(wfc: WaveFunctionCollapse) -> None:
    assert sum(wfc.tile_weights.values()) == pytest.approx(1.0)
    assert len(wfc.all_tiles) == 16


# Testing the "_compute_neighbors" method from the "WaveFunctionCollapse" class.


def test_neighbors_only_contain_tiles_that_match_the_edge(wfc: WaveFunctionCollapse) -> None:
    tile = Tile((("A", "A"), ("A", "A")))
    matching = Tile((("A", "A"), ("A", "A")))

    assert matching in wfc.neighbors[tile]["up"]
    assert all(tile.up == other.down for other in wfc.neighbors[tile]["up"])
    assert all(tile.left == other.right for other in wfc.neighbors[tile]["left"])


# Testing the "_initialize_grid" method from the "WaveFunctionCollapse" class.


def test_initialize_grid_starts_every_cell_open(wfc: WaveFunctionCollapse) -> None:
    assert len(wfc.grid) == 6
    assert all(
        not cell.collapsed and cell.options == wfc.tile_set
        for row in wfc.grid
        for cell in row
    )


# Testing the "propagate" method from the "WaveFunctionCollapse" class.


def test_propagate_does_nothing_at_zero_depth(wfc: WaveFunctionCollapse) -> None:
    before = [len(cell.options) for row in wfc.grid for cell in row]

    wfc.propagate(y=2, x=2, recursion_depth=0)

    assert [len(cell.options) for row in wfc.grid for cell in row] == before


def test_propagate_narrows_the_neighbors_of_a_collapsed_cell(wfc: WaveFunctionCollapse) -> None:
    wfc._collapse_grid_cell(y=2, x=2)
    collapsed_tile = wfc.grid[2][2].tile
    assert collapsed_tile is not None

    wfc.propagate(y=2, x=2, recursion_depth=1)

    neighbor = wfc.grid[1][2]
    assert neighbor.options <= wfc.neighbors[collapsed_tile]["up"]
    assert not any(cell.propagated for row in wfc.grid for cell in row)


def test_propagate_handles_open_cells_at_the_grid_edge(wfc: WaveFunctionCollapse) -> None:
    wfc.propagate(y=0, x=0, recursion_depth=2)

    assert not any(cell.propagated for row in wfc.grid for cell in row)


# Testing the "_find_min_entropy_cells" method from the "WaveFunctionCollapse" class.


def test_find_min_entropy_cells_returns_all_open_cells_when_tied(
    wfc: WaveFunctionCollapse,
) -> None:
    candidates = wfc._find_min_entropy_cells()

    assert len(candidates) == 36


def test_find_min_entropy_cells_prefers_the_most_constrained(wfc: WaveFunctionCollapse) -> None:
    wfc.grid[0][0].options = {next(iter(wfc.tile_set))}

    assert wfc._find_min_entropy_cells() == [(0, 0)]


def test_find_min_entropy_cells_is_empty_when_everything_is_collapsed(
    wfc: WaveFunctionCollapse,
) -> None:
    for row in wfc.grid:
        for cell in row:
            cell.collapsed = True

    assert wfc._find_min_entropy_cells() == []


# Testing the "_collapse_grid_cell" method from the "WaveFunctionCollapse" class.


def test_collapse_grid_cell_picks_one_of_the_options(wfc: WaveFunctionCollapse) -> None:
    wfc._collapse_grid_cell(y=0, x=0)

    cell = wfc.grid[0][0]
    assert cell.collapsed is True
    assert cell.tile in wfc.tile_set
    assert cell.options == set()
    assert cell.superposition_tile is None


def test_collapse_grid_cell_raises_for_a_cell_without_options(wfc: WaveFunctionCollapse) -> None:
    wfc.grid[1][4].options = set()

    with pytest.raises(ContradictionError, match="row 1, column 4"):
        wfc._collapse_grid_cell(y=1, x=4)


# Testing the "_draw_step" method from the "WaveFunctionCollapse" class.


def test_draw_step_is_true_without_a_visualizer(wfc: WaveFunctionCollapse) -> None:
    assert wfc._draw_step() is True


class _StopVisualizer:
    """A visualizer stand-in that asks to stop on its first frame."""

    def __init__(self) -> None:
        """Count the frames drawn, so the test can check when collapse stopped."""
        self.frames = 0

    def visualize(self, grid: Any) -> bool:
        """Count the frame, and ask to stop.

        Args:
            grid (Any): The grid being drawn, which is not used.

        Returns:
            keep_running (bool): Always False.
        """
        self.frames += 1

        return False


def test_draw_step_passes_the_stop_request_from_the_visualizer(
    small_config: ConfigModel, stripe_bitmap: list[list[str]]
) -> None:
    visualizer = _StopVisualizer()
    wfc = WaveFunctionCollapse(
        config=small_config,
        bitmap=stripe_bitmap,
        color_mapping=_COLOR_MAPPING,
        visualizer=visualizer,  # type: ignore[arg-type]
        rng=random.Random(0),
    )

    assert wfc._draw_step() is False


# Testing the "collapse_grid" method from the "WaveFunctionCollapse" class.


def test_collapse_grid_collapses_every_cell(wfc: WaveFunctionCollapse) -> None:
    wfc.collapse_grid()

    assert all(cell.collapsed for row in wfc.grid for cell in row)
    assert all(cell.tile is not None for row in wfc.grid for cell in row)


def test_collapse_grid_stops_when_the_visualizer_asks(
    small_config: ConfigModel, stripe_bitmap: list[list[str]]
) -> None:
    visualizer = _StopVisualizer()
    wfc = WaveFunctionCollapse(
        config=small_config,
        bitmap=stripe_bitmap,
        color_mapping=_COLOR_MAPPING,
        visualizer=visualizer,  # type: ignore[arg-type]
        rng=random.Random(0),
    )

    wfc.collapse_grid()

    assert visualizer.frames == 1
    assert sum(cell.collapsed for row in wfc.grid for cell in row) == 1


def test_collapse_grid_raises_on_contradiction(wfc: WaveFunctionCollapse) -> None:
    wfc.grid[0][0].options = set()

    with pytest.raises(ContradictionError):
        wfc.collapse_grid()
