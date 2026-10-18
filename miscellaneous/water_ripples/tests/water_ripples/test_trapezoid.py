"""Tests for the trapezoid module."""

from typing import Any

import numpy as np
import pygame as pg

from water_ripples.config_model import ConfigModel
from water_ripples.trapezoid import TrapezoidRipples


def _make_trapezoid(config_data: dict[str, Any], **trapezoid: float) -> TrapezoidRipples:
    """Create a trapezoid simulation with the given trapezoid settings.

    Args:
        config_data (dict[str, Any]): Raw configuration to modify.
        **trapezoid (float): Trapezoid settings to override, such as perspective_exponent.

    Returns:
        simulation (TrapezoidRipples): The simulation, ready to use.
    """
    config_data["trapezoid"].update(trapezoid)
    simulation = TrapezoidRipples(config=ConfigModel.model_validate(config_data))

    return simulation


# Testing the "_compute_row_geometry" method from the "TrapezoidRipples" class.


def test_row_geometry_has_one_entry_per_row_and_ends_at_trapezoid_bottom(
    config_data: dict[str, Any],
) -> None:
    simulation = _make_trapezoid(config_data)

    geometry = simulation.row_geometry

    assert len(geometry) == simulation.number_of_rows
    assert geometry[-1].y_bottom == 200
    assert all(a.y_top <= b.y_top for a, b in zip(geometry, geometry[1:]))


def test_perspective_makes_bottom_rows_taller(config_data: dict[str, Any]) -> None:
    flat = _make_trapezoid(config_data, perspective_exponent=0.0)
    perspective = _make_trapezoid(config_data, perspective_exponent=2.0)

    flat_heights = [g.y_bottom - g.y_top for g in flat.row_geometry]
    perspective_heights = [g.y_bottom - g.y_top for g in perspective.row_geometry]

    assert max(flat_heights) - min(flat_heights) <= 1
    assert perspective_heights[-1] > perspective_heights[0]


# Testing the "_mouse_y_to_grid_y" method from the "TrapezoidRipples" class.


def test_mouse_y_to_grid_y_finds_row_containing_position(config_data: dict[str, Any]) -> None:
    simulation = _make_trapezoid(config_data)
    first_row = simulation.row_geometry[0]

    assert simulation._mouse_y_to_grid_y(my=first_row.y_top) == 0


def test_mouse_y_to_grid_y_maps_below_trapezoid_to_last_row(config_data: dict[str, Any]) -> None:
    simulation = _make_trapezoid(config_data)

    assert simulation._mouse_y_to_grid_y(my=10_000) == simulation.number_of_rows - 1


# Testing the "_mouse_x_to_grid_x" method from the "TrapezoidRipples" class.


def test_mouse_x_to_grid_x_maps_row_edges_to_first_and_last_column(
    config_data: dict[str, Any],
) -> None:
    simulation = _make_trapezoid(config_data)
    geometry = simulation.row_geometry[-1]

    first_column = simulation._mouse_x_to_grid_x(mx=geometry.x_left, grid_y=-1)
    last_column = simulation._mouse_x_to_grid_x(mx=geometry.x_right - 1, grid_y=-1)

    assert first_column == 0
    assert last_column == simulation.number_of_columns - 1


# Testing the "_mouse_to_grid" method from the "TrapezoidRipples" class.


def test_mouse_to_grid_returns_column_and_row(config_data: dict[str, Any]) -> None:
    simulation = _make_trapezoid(config_data)
    geometry = simulation.row_geometry[3]

    grid_position = simulation._mouse_to_grid(mx=geometry.x_left, my=geometry.y_top)

    assert grid_position == (0, 3)


# Testing the "_map_state_to_rgba" method from the "TrapezoidRipples" class.


def test_map_state_to_rgba_is_fully_opaque(config_data: dict[str, Any]) -> None:
    simulation = _make_trapezoid(config_data)
    simulation.current_state[:] = 50.0

    rgba_array = simulation._map_state_to_rgba()

    assert rgba_array.shape == (simulation.number_of_rows, simulation.number_of_columns, 4)
    assert np.all(rgba_array[..., 3] == 255)


# Testing the "_render_rows" method from the "TrapezoidRipples" class.


def test_render_rows_skips_rows_without_width(config_data: dict[str, Any]) -> None:
    simulation = _make_trapezoid(config_data, x_top_left=0.5, x_top_right=0.5)
    rgba_array = simulation._map_state_to_rgba()

    simulation._render_rows(rgba_array=rgba_array)

    assert pg.surfarray.array3d(simulation.screen).max() > 0


# Testing the "_draw_frame" method from the "TrapezoidRipples" class.


def test_draw_frame_runs(config_data: dict[str, Any]) -> None:
    simulation = _make_trapezoid(config_data)

    simulation._draw_frame()
