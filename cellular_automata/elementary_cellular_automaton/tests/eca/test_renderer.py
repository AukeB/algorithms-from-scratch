"""Tests for the renderer module."""

from typing import Any

import pytest

from eca.config.config_model import ConfigModel
from eca.grid import Grid
from eca.renderer import Renderer


@pytest.fixture
def renderer(config_data: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> Renderer:
    """Provides a Renderer with a fixed, known window size.

    Args:
        config_data (dict[str, Any]): Raw configuration used to build the renderer.
        monkeypatch (pytest.MonkeyPatch): Used to fix the window size.

    Returns:
        renderer (Renderer): A renderer backed by the dummy pygame display.
    """
    monkeypatch.setattr(
        "eca.renderer.get_window_size_from_screen_resolution",
        lambda: (1000, 800),
    )
    config = ConfigModel(**config_data)

    renderer = Renderer(config=config)

    return renderer


# Testing the "__init__" method from the "Renderer" class.


def test_init_snaps_cell_size_to_integer_pixels(renderer: Renderer) -> None:
    assert isinstance(renderer._cell_size, int)
    assert renderer._grid_size == renderer._cell_size * 5


# Testing the "_snap_to_pixel_grid" method from the "Renderer" class.


def test_snap_to_pixel_grid_logs_adjustment(
    renderer: Renderer, caplog: pytest.LogCaptureFixture
) -> None:
    renderer._cell_size = 2.4
    renderer._grid_size = 12.0

    with caplog.at_level("INFO", logger="eca.renderer"):
        renderer._snap_to_pixel_grid()

    assert "cell-size snapping" in caplog.text
    assert renderer._cell_size == 2


def test_snap_to_pixel_grid_skips_logging_when_not_verbose(
    renderer: Renderer, caplog: pytest.LogCaptureFixture
) -> None:
    renderer._cell_size = 2.4
    renderer._grid_size = 12.0

    with caplog.at_level("INFO", logger="eca.renderer"):
        renderer._snap_to_pixel_grid(verbose=False)

    assert "cell-size snapping" not in caplog.text
    assert renderer._cell_size == 2


# Testing the "tick" method from the "Renderer" class.


def test_tick_returns_elapsed_seconds(renderer: Renderer) -> None:
    dt = renderer.tick(fps=1000)

    assert dt >= 0.0


# Testing the "render" method from the "Renderer" class.


def test_render_draws_grid_with_gridlines(
    renderer: Renderer, config_data: dict[str, Any]
) -> None:
    renderer._show_gridlines = True
    grid = Grid(config=ConfigModel(**config_data))
    grid.initialize()

    renderer.render(grid=grid)

    assert renderer._screen.get_size() == (
        renderer._screen_size.width,
        renderer._screen_size.height,
    )
