"""Tests for the perlin_noise module."""

from typing import Any, Callable

import numpy as np
import pygame as pg

from perlin_noise.config_model import ConfigModel
from perlin_noise.perlin_noise import PerlinNoise


# Testing the "__init__" method from the "PerlinNoise" class.


def test_init_sets_grid_dimensions(config: ConfigModel) -> None:
    perlin_noise = PerlinNoise(config=config)

    assert tuple(perlin_noise.gradient_grid_dimensions) == (6, 6)
    assert tuple(perlin_noise.noise_grid_dimensions) == (50, 50)
    assert perlin_noise.step_size == 0.1


def test_init_with_same_seed_gives_same_gradients(config: ConfigModel) -> None:
    first = PerlinNoise(config=config)
    second = PerlinNoise(config=config)

    assert np.array_equal(
        first._populate_gradient_grid(), second._populate_gradient_grid()
    )


def test_init_without_seed_still_creates_generator(raw_config: dict[str, Any]) -> None:
    raw_config["grid"]["random_seed"] = None
    config = ConfigModel.model_validate(raw_config)

    perlin_noise = PerlinNoise(config=config)

    assert perlin_noise.rng is not None


# Testing the "_populate_gradient_grid" method from the "PerlinNoise" class.


def test_populate_gradient_grid_has_unit_vectors(config: ConfigModel) -> None:
    perlin_noise = PerlinNoise(config=config)

    gradient_grid = perlin_noise._populate_gradient_grid()

    assert gradient_grid.shape == (6, 6, 2)
    assert np.allclose(np.linalg.norm(gradient_grid, axis=-1), 1.0)


# Testing the "_compute_noise_grid" method from the "PerlinNoise" class.


def test_compute_noise_grid_is_zero_at_lattice_nodes(config: ConfigModel) -> None:
    perlin_noise = PerlinNoise(config=config)
    perlin_noise.generate()

    noise_grid = perlin_noise._compute_noise_grid(interpolate=True)

    assert noise_grid.shape == (50, 50)
    assert noise_grid[0, 0] == 0.0
    assert np.all(np.abs(noise_grid) <= 1.0)


def test_compute_noise_grid_without_interpolation_differs(config: ConfigModel) -> None:
    perlin_noise = PerlinNoise(config=config)
    perlin_noise.generate()

    interpolated = perlin_noise._compute_noise_grid(interpolate=True)
    averaged = perlin_noise._compute_noise_grid(interpolate=False)

    assert averaged.shape == interpolated.shape
    assert not np.allclose(averaged, interpolated)


def test_compute_noise_grid_works_with_original_smoothing(raw_config: dict[str, Any]) -> None:
    raw_config["grid"]["smoothing_version"] = "original"
    config = ConfigModel.model_validate(raw_config)
    perlin_noise = PerlinNoise(config=config)

    perlin_noise.generate()

    assert np.all(np.isfinite(perlin_noise.noise_grid))


# Testing the "generate" method from the "PerlinNoise" class.


def test_generate_fills_gradient_and_noise_grids(config: ConfigModel) -> None:
    perlin_noise = PerlinNoise(config=config)

    perlin_noise.generate()

    assert perlin_noise.gradient_grid.shape == (6, 6, 2)
    assert perlin_noise.noise_grid.shape == (50, 50)
    assert perlin_noise.noise_grid.any()


# Testing the "_handle_events" method from the "PerlinNoise" class.


def test_handle_events_keeps_running_for_other_keys(
    config: ConfigModel, scripted_input: Callable[..., None]
) -> None:
    perlin_noise = PerlinNoise(config=config)
    scripted_input(event_batches=[[pg.event.Event(pg.KEYDOWN, key=pg.K_a)]])

    assert perlin_noise._handle_events() is True


def test_handle_events_stops_on_window_close(
    config: ConfigModel, scripted_input: Callable[..., None]
) -> None:
    perlin_noise = PerlinNoise(config=config)
    scripted_input(event_batches=[[pg.event.Event(pg.QUIT)]])

    assert perlin_noise._handle_events() is False


def test_handle_events_stops_on_escape(
    config: ConfigModel, scripted_input: Callable[..., None]
) -> None:
    perlin_noise = PerlinNoise(config=config)
    scripted_input(event_batches=[[pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE)]])

    assert perlin_noise._handle_events() is False


# Testing the "run" method from the "PerlinNoise" class.


def test_run_generates_then_exits_when_window_closes(
    config: ConfigModel, scripted_input: Callable[..., None]
) -> None:
    perlin_noise = PerlinNoise(config=config)
    scripted_input(event_batches=[[], [pg.event.Event(pg.QUIT)]])

    perlin_noise.run()

    assert perlin_noise.noise_grid.any()
