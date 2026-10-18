"""Tests for the simulation module."""

from typing import Any, Callable

import numpy as np
import pygame as pg

from water_ripples.baseline import BaselineRipples
from water_ripples.config_model import ConfigModel
from water_ripples.simulation import (
    clamp,
    colorize,
    propagate_with_numba,
    to_trapezoid_pixels,
)


# Testing the "propagate_with_numba" function.


def test_propagate_with_numba_applies_ripple_formula_and_damping() -> None:
    previous_state = np.zeros((3, 3), dtype=np.float32)
    previous_state[0, 1] = 2.0
    current_state = np.zeros((3, 3), dtype=np.float32)

    propagate_with_numba(
        current_state=current_state,
        previous_state=previous_state,
        damping=0.5,
    )

    # Neighbor sum is 2, so (2 / 2 - 0) * 0.5 at the only interior cell.
    assert current_state[1, 1] == 0.5


# Testing the "colorize" function.


def test_colorize_returns_uint8_rgb_array() -> None:
    state = np.zeros((2, 3), dtype=np.float32)

    rgb_array = colorize(state=state, maximum_brightness=255, floor=0.0, span=1.0)

    assert rgb_array.shape == (2, 3, 3)
    assert rgb_array.dtype == np.uint8


def test_colorize_clips_values_above_maximum_brightness() -> None:
    at_maximum = np.full((1, 1), 255.0, dtype=np.float32)
    above_maximum = np.full((1, 1), 300.0, dtype=np.float32)

    rgb_at_maximum = colorize(at_maximum, 255, floor=0.1, span=0.8)
    rgb_above_maximum = colorize(above_maximum, 255, floor=0.1, span=0.8)

    assert np.array_equal(rgb_at_maximum, rgb_above_maximum)


# Testing the "clamp" function.


def test_clamp_limits_value_to_range() -> None:
    assert clamp(-1, 0, 5) == 0
    assert clamp(7, 0, 5) == 5
    assert clamp(3, 0, 5) == 3


# Testing the "to_trapezoid_pixels" function.


def test_to_trapezoid_pixels_scales_y_by_height_and_x_by_width(
    config_data: dict[str, Any],
) -> None:
    normalized = ConfigModel.model_validate(config_data).trapezoid

    trapezoid = to_trapezoid_pixels(
        normalized=normalized, window_width=320, window_height=200
    )

    assert trapezoid.y_top == 80.0
    assert trapezoid.y_bottom == 200.0
    assert trapezoid.x_bottom_left == 64.0
    assert trapezoid.x_top_right == 320.0


# Testing the "_splash" method from the "RippleSimulation" class.


def test_splash_disturbs_square_around_cell(config_data: dict[str, Any]) -> None:
    simulation = BaselineRipples(config=ConfigModel.model_validate(config_data))
    simulation.previous_state[:] = 0.0

    simulation._splash(grid_x=2, grid_y=2)

    assert simulation.previous_state[1, 1] == simulation.wave_brightness
    assert simulation.previous_state[3, 3] == 0.0


def test_splash_never_disturbs_the_border(config_data: dict[str, Any]) -> None:
    simulation = BaselineRipples(config=ConfigModel.model_validate(config_data))
    simulation.previous_state[:] = 0.0

    simulation._splash(grid_x=0, grid_y=0)
    simulation._splash(grid_x=10_000, grid_y=10_000)

    assert simulation.previous_state[0, :].sum() == 0.0
    assert simulation.previous_state[:, 0].sum() == 0.0
    assert simulation.previous_state[-1, :].sum() == 0.0
    assert simulation.previous_state[:, -1].sum() == 0.0


# Testing the "_propagate" method from the "RippleSimulation" class.


def test_propagate_swaps_the_two_grids(config_data: dict[str, Any]) -> None:
    simulation = BaselineRipples(config=ConfigModel.model_validate(config_data))
    previous_before = simulation.previous_state
    current_before = simulation.current_state

    simulation._propagate()

    assert simulation.previous_state is current_before
    assert simulation.current_state is previous_before


# Testing the "execute" method from the "RippleSimulation" class.


def test_execute_exits_when_window_is_closed(
    config_data: dict[str, Any],
    scripted_input: Callable[..., None],
) -> None:
    simulation = BaselineRipples(config=ConfigModel.model_validate(config_data))
    scripted_input(event_batches=[[pg.event.Event(pg.QUIT)]])

    simulation.execute()


def test_execute_exits_on_escape_and_handles_other_keys(
    config_data: dict[str, Any],
    scripted_input: Callable[..., None],
) -> None:
    simulation = BaselineRipples(config=ConfigModel.model_validate(config_data))
    scripted_input(
        event_batches=[
            [pg.event.Event(pg.KEYDOWN, key=pg.K_a)],
            [pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE)],
        ]
    )

    simulation.execute()


def test_execute_disturbs_state_while_mouse_is_held(
    config_data: dict[str, Any],
    scripted_input: Callable[..., None],
) -> None:
    simulation = BaselineRipples(config=ConfigModel.model_validate(config_data))
    simulation.previous_state[:] = 0.0
    scripted_input(
        event_batches=[[], [pg.event.Event(pg.QUIT)]],
        mouse_pressed=True,
        mouse_pos=(160, 100),
    )

    simulation.execute()

    # The splash is propagated and swapped into previous_state, so it has spread outwards.
    assert simulation.previous_state.max() > 0
