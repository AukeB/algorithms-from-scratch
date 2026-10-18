"""Tests for the baseline module."""

from typing import Any

import numpy as np
import pygame as pg
import pytest

from water_ripples.baseline import BaselineRipples
from water_ripples.config_model import ConfigModel


def _make_baseline(config_data: dict[str, Any], **baseline: str) -> BaselineRipples:
    """Create a baseline simulation with the given baseline modes.

    Args:
        config_data (dict[str, Any]): Raw configuration to modify.
        **baseline (str): Baseline options to override, such as render_mode.

    Returns:
        simulation (BaselineRipples): The simulation, ready to use.
    """
    config_data["baseline"].update(baseline)
    simulation = BaselineRipples(config=ConfigModel.model_validate(config_data))

    return simulation


# Testing the "__init__" method from the "BaselineRipples" class.


def test_init_reads_modes_from_config(config_data: dict[str, Any]) -> None:
    simulation = _make_baseline(config_data, propagate_mode="numpy")

    assert simulation.propagate_mode == "numpy"
    assert simulation.render_mode == "surfarray"
    assert simulation.rgb_mode == "scaled_colormap"


# Testing the propagate modes through the "_compute_next_state" method.


@pytest.mark.parametrize("propagate_mode", ["numba", "numpy", "iterative"])
def test_compute_next_state_matches_numba_for_every_mode(
    config_data: dict[str, Any], propagate_mode: str
) -> None:
    reference = _make_baseline(config_data, propagate_mode="numba")
    candidate = _make_baseline(config_data, propagate_mode=propagate_mode)

    rng = np.random.default_rng(0)
    random_state = rng.uniform(-50, 50, size=reference.previous_state.shape)
    reference.previous_state[:] = random_state
    candidate.previous_state[:] = random_state

    reference._compute_next_state()
    candidate._compute_next_state()

    assert np.allclose(reference.current_state, candidate.current_state, atol=1e-4)


# Testing the "_map_state_to_rgb" method from the "BaselineRipples" class.


@pytest.mark.parametrize("mode", ["grayscale", "colormap", "scaled_colormap"])
def test_map_state_to_rgb_returns_uint8_rgb(config_data: dict[str, Any], mode: str) -> None:
    simulation = _make_baseline(config_data)
    simulation.current_state[:] = 100.0

    rgb_array = simulation._map_state_to_rgb(mode=mode)

    assert rgb_array.shape == (simulation.number_of_rows, simulation.number_of_columns, 3)
    assert rgb_array.dtype == np.uint8


def test_map_state_to_rgb_grayscale_repeats_the_state(config_data: dict[str, Any]) -> None:
    simulation = _make_baseline(config_data)
    simulation.current_state[:] = 100.0

    rgb_array = simulation._map_state_to_rgb(mode="grayscale")

    assert np.all(rgb_array == 100)


# Testing the "_render_state" method from the "BaselineRipples" class.


@pytest.mark.parametrize("render_mode", ["surfarray", "rectangle"])
def test_render_state_draws_both_modes(config_data: dict[str, Any], render_mode: str) -> None:
    simulation = _make_baseline(config_data, render_mode=render_mode)
    rgb_array = np.full((simulation.number_of_rows, simulation.number_of_columns, 3), 200, dtype=np.uint8)

    simulation._render_state(rgb_array=rgb_array, mode=render_mode)

    assert pg.surfarray.array3d(simulation.screen).max() > 0


# Testing the "_mouse_to_grid" method from the "BaselineRipples" class.


def test_mouse_to_grid_divides_by_uniform_cell_size(config_data: dict[str, Any]) -> None:
    simulation = _make_baseline(config_data)

    grid_position = simulation._mouse_to_grid(mx=45, my=30)

    assert grid_position == (2, 1)


# Testing the "_draw_frame" method from the "BaselineRipples" class.


@pytest.mark.parametrize("rgb_mode", ["grayscale", "colormap", "scaled_colormap"])
def test_draw_frame_runs_for_every_rgb_mode(config_data: dict[str, Any], rgb_mode: str) -> None:
    simulation = _make_baseline(config_data, rgb_mode=rgb_mode)

    simulation._draw_frame()
