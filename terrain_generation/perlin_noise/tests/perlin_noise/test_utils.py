"""Tests for the utils module."""

import pygame as pg
import pytest

from perlin_noise.utils import (
    get_window_size_from_screen_resolution,
    lerp_color,
    smooth_perlin_polynomial,
)


# Testing the "get_window_size_from_screen_resolution" function.


def test_window_size_scales_the_desktop_size(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(1920, 1080)])

    window_size = get_window_size_from_screen_resolution()

    assert window_size == (1824, 1026)


def test_window_size_clamps_to_minimum(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(100, 100)])

    window_size = get_window_size_from_screen_resolution()

    assert window_size == (400, 300)


def test_window_size_initializes_display_when_needed(monkeypatch: pytest.MonkeyPatch) -> None:
    initialized: list[bool] = []
    monkeypatch.setattr(pg.display, "get_init", lambda: False)
    monkeypatch.setattr(pg.display, "init", lambda: initialized.append(True))
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(1920, 1080)])

    get_window_size_from_screen_resolution()

    assert initialized == [True]


# Testing the "lerp_color" function.


def test_lerp_color_is_white_at_zero() -> None:
    assert lerp_color((10, 20, 30), 0.0) == (255, 255, 255)


def test_lerp_color_is_the_target_at_one() -> None:
    assert lerp_color((10, 20, 30), 1.0) == (10, 20, 30)


def test_lerp_color_blends_halfway() -> None:
    assert lerp_color((0, 0, 0), 0.5) == (127, 127, 127)


# Testing the "smooth_perlin_polynomial" function.


@pytest.mark.parametrize("smoothing_version", ["original", "revised"])
def test_smooth_perlin_polynomial_fixes_the_endpoints(smoothing_version: str) -> None:
    assert smooth_perlin_polynomial(0.0, smoothing_version) == 0.0
    assert smooth_perlin_polynomial(1.0, smoothing_version) == 1.0


def test_smooth_perlin_polynomial_is_symmetric_around_one_half() -> None:
    assert smooth_perlin_polynomial(0.5, "original") == pytest.approx(0.5)
    assert smooth_perlin_polynomial(0.5, "revised") == pytest.approx(0.5)


def test_smooth_perlin_polynomial_versions_differ() -> None:
    original = smooth_perlin_polynomial(0.25, "original")
    revised = smooth_perlin_polynomial(0.25, "revised")

    assert original != pytest.approx(revised)
