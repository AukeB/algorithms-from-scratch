"""Tests for the image_overlay module."""

from typing import Any

import numpy as np
import pygame as pg
import pytest

from water_ripples.config_model import ConfigModel
from water_ripples.image_overlay import ImageRipples


@pytest.fixture(name="simulation")
def fixture_simulation(config_data: dict[str, Any]) -> ImageRipples:
    """Provide an image simulation, with a mask that is resized to the window.

    Args:
        config_data (dict[str, Any]): The raw configuration.

    Returns:
        simulation (ImageRipples): The simulation, ready to use.
    """
    config_data["variant"] = "image"
    simulation = ImageRipples(config=ConfigModel.model_validate(config_data))

    return simulation


# Testing the "__init__" method from the "ImageRipples" class.


def test_init_loads_image_and_resizes_mask_to_window(simulation: ImageRipples) -> None:
    assert simulation.background_image.get_size() == (320, 200)
    assert simulation.mask.shape == (200, 320)
    assert simulation.mask.dtype == bool


# Testing the "_compute_vertical_scaling" method from the "ImageRipples" class.


def test_compute_vertical_scaling_is_zero_for_top_row(simulation: ImageRipples) -> None:
    assert simulation._compute_vertical_scaling(y=0) == 0.0


def test_compute_vertical_scaling_grows_toward_bottom_rows(simulation: ImageRipples) -> None:
    projected = [simulation._compute_vertical_scaling(y=y) for y in range(10)]

    assert all(a < b for a, b in zip(projected, projected[1:]))


# Testing the "_inverse_vertical_scaling" method from the "ImageRipples" class.


def test_inverse_vertical_scaling_undoes_forward_scaling(simulation: ImageRipples) -> None:
    projected = simulation._compute_vertical_scaling(y=3.0)

    row = simulation._inverse_vertical_scaling(y_adjusted=projected)

    assert row == pytest.approx(3.0)


# Testing the "_row_x_bounds" method from the "ImageRipples" class.


def test_row_x_bounds_at_top_match_trapezoid_top_corners(simulation: ImageRipples) -> None:
    x_left, x_right = simulation._row_x_bounds(y_adjusted=0.0)

    assert x_left == simulation.trapezoid.x_top_left
    assert x_right == simulation.trapezoid.x_top_right


# Testing the "_mouse_y_to_grid_y" method from the "ImageRipples" class.


def test_mouse_y_to_grid_y_is_none_outside_trapezoid(simulation: ImageRipples) -> None:
    assert simulation._mouse_y_to_grid_y(my=0) is None
    assert simulation._mouse_y_to_grid_y(my=199 + 1000) is None


def test_mouse_y_to_grid_y_returns_row_inside_trapezoid(simulation: ImageRipples) -> None:
    grid_y = simulation._mouse_y_to_grid_y(my=150)

    assert grid_y is not None
    assert 0 <= grid_y < simulation.number_of_rows


# Testing the "_mouse_x_to_grid_x" method from the "ImageRipples" class.


def test_mouse_x_to_grid_x_clamps_to_columns(simulation: ImageRipples) -> None:
    assert simulation._mouse_x_to_grid_x(mx=-500, grid_y=5) == 0
    assert simulation._mouse_x_to_grid_x(mx=5000, grid_y=5) == simulation.number_of_columns - 1


# Testing the "_mouse_to_grid" method from the "ImageRipples" class.


def test_mouse_to_grid_is_none_outside_trapezoid(simulation: ImageRipples) -> None:
    assert simulation._mouse_to_grid(mx=10, my=0) is None


def test_mouse_to_grid_returns_column_and_row_inside_trapezoid(
    simulation: ImageRipples,
) -> None:
    grid_position = simulation._mouse_to_grid(mx=160, my=150)

    assert grid_position is not None
    grid_x, grid_y = grid_position
    assert 0 <= grid_x < simulation.number_of_columns
    assert 0 <= grid_y < simulation.number_of_rows


def test_handle_mouse_ignores_clicks_outside_trapezoid(
    simulation: ImageRipples, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pg.mouse, "get_pos", lambda: (10, 0))
    simulation.previous_state[:] = 0.0

    simulation._handle_mouse()

    assert simulation.previous_state.sum() == 0.0


# Testing the "_map_state_to_rgba" method from the "ImageRipples" class.


def test_map_state_to_rgba_is_transparent_where_water_is_flat(
    simulation: ImageRipples,
) -> None:
    simulation.current_state[:] = 0.0

    rgba_array = simulation._map_state_to_rgba()

    assert rgba_array.shape == (simulation.number_of_rows, simulation.number_of_columns, 4)
    assert np.all(rgba_array[..., 3] == 0)


def test_map_state_to_rgba_is_opaque_at_wave_peaks(simulation: ImageRipples) -> None:
    simulation.current_state[:] = 255.0

    rgba_array = simulation._map_state_to_rgba()

    assert np.all(rgba_array[..., 3] == 255)


# Testing the "_render_state" method from the "ImageRipples" class.


def test_render_state_draws_nothing_outside_the_mask(simulation: ImageRipples) -> None:
    simulation.mask = np.zeros_like(simulation.mask)
    simulation.screen.fill((0, 0, 0))
    simulation.current_state[:] = 255.0
    rgba_array = simulation._map_state_to_rgba()

    simulation._render_state(rgba_array=rgba_array)

    assert pg.surfarray.array3d(simulation.screen).max() == 0


def test_render_state_draws_inside_the_mask(simulation: ImageRipples) -> None:
    simulation.mask = np.ones_like(simulation.mask)
    simulation.screen.fill((0, 0, 0))
    simulation.current_state[:] = 255.0
    rgba_array = simulation._map_state_to_rgba()

    simulation._render_state(rgba_array=rgba_array)

    assert pg.surfarray.array3d(simulation.screen).max() > 0


# Testing the "_draw_frame" method from the "ImageRipples" class.


def test_draw_frame_runs(simulation: ImageRipples) -> None:
    simulation._draw_frame()
