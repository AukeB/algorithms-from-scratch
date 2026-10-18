"""Tests for the pn_visualizer module."""

import itertools

import numpy as np
import pygame as pg
import pytest

from perlin_noise.config_model import ConfigModel
from perlin_noise.pn_visualizer import ButtonState, PNVisualizer, VisibilityState


@pytest.fixture(name="visualizer")
def fixture_visualizer(config: ConfigModel) -> PNVisualizer:
    """Provide a visualizer with a headless window.

    Args:
        config (ConfigModel): The validated configuration.

    Returns:
        visualizer (PNVisualizer): The visualizer, ready to draw.
    """
    visualizer = PNVisualizer(config=config)

    return visualizer


@pytest.fixture(name="unit_gradients")
def fixture_unit_gradients() -> np.ndarray:
    """Provide unit gradient vectors for a 6 x 6 grid of nodes.

    Returns:
        gradient_grid (np.ndarray): Array of shape (6, 6, 2).
    """
    angles = np.linspace(0.0, np.pi, 36).reshape(6, 6)
    gradient_grid = np.stack([np.cos(angles), np.sin(angles)], axis=-1)

    return gradient_grid


# Testing the "__init__" method from the "PNVisualizer" class.


def test_init_sizes_the_grid_to_fit_the_window(visualizer: PNVisualizer) -> None:
    expected_grid_size = min(
        visualizer.screen_size.width - 2 * visualizer.margin_size,
        visualizer.screen_size.height - 2 * visualizer.margin_size,
    )

    assert visualizer.grid_size == expected_grid_size
    assert visualizer.cell_size == expected_grid_size / 5


# Testing the "register_buttons" method from the "PNVisualizer" class.


def test_register_buttons_returns_the_three_toggles(visualizer: PNVisualizer) -> None:
    buttons = visualizer.register_buttons()

    assert isinstance(buttons, ButtonState)
    assert buttons.grid is not buttons.noise_vectors


# Testing the "from_buttons" method from the "VisibilityState" class.


def test_from_buttons_reads_each_toggle(visualizer: PNVisualizer) -> None:
    buttons = visualizer.register_buttons()
    buttons.grid.value = True
    buttons.gradient_vectors.value = False
    buttons.noise_vectors.value = True

    visibility = VisibilityState.from_buttons(buttons)

    assert visibility == VisibilityState(
        show_grid=True, show_gradients=False, show_noise=True
    )


# Testing the "_draw_grid_lines" method from the "PNVisualizer" class.


def test_draw_grid_lines_draws_on_the_screen(visualizer: PNVisualizer) -> None:
    visualizer.screen.fill((0, 0, 0))

    visualizer._draw_grid_lines()

    assert pg.surfarray.array3d(visualizer.screen).max() > 0


# Testing the "_draw_gradient_vectors" method from the "PNVisualizer" class.


def test_draw_gradient_vectors_draws_on_the_screen(
    visualizer: PNVisualizer, unit_gradients: np.ndarray
) -> None:
    visualizer.screen.fill((0, 0, 0))

    visualizer._draw_gradient_vectors(gradient_grid=unit_gradients)

    assert pg.surfarray.array3d(visualizer.screen).max() > 0


# Testing the "_draw_noise_cells" method from the "PNVisualizer" class.


def test_draw_noise_cells_handles_an_all_zero_grid(visualizer: PNVisualizer) -> None:
    visualizer.screen.fill((0, 0, 0))

    visualizer._draw_noise_cells(noise_grid=np.zeros((5, 5)))

    assert pg.surfarray.array3d(visualizer.screen).max() > 0


def test_draw_noise_cells_shades_positive_and_negative_values(
    visualizer: PNVisualizer,
) -> None:
    noise_grid = np.array([[-1.0, 1.0], [0.5, -0.5]])
    visualizer.screen.fill((0, 0, 0))

    visualizer._draw_noise_cells(noise_grid=noise_grid)

    assert pg.surfarray.array3d(visualizer.screen).max() > 0


# Testing the "draw_frame" method from the "PNVisualizer" class.


@pytest.mark.parametrize(
    ("show_grid", "show_gradients", "show_noise"),
    list(itertools.product([False, True], repeat=3)),
)
def test_draw_frame_draws_every_combination_of_layers(
    visualizer: PNVisualizer,
    unit_gradients: np.ndarray,
    show_grid: bool,
    show_gradients: bool,
    show_noise: bool,
) -> None:
    visibility = VisibilityState(
        show_grid=show_grid, show_gradients=show_gradients, show_noise=show_noise
    )
    noise_grid = np.linspace(-1.0, 1.0, 25).reshape(5, 5)

    visualizer.draw_frame(
        gradient_grid=unit_gradients,
        noise_grid=noise_grid,
        visibility=visibility,
    )
