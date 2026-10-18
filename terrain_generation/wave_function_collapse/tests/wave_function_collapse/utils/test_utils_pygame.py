"""Tests for the utils_pygame module."""

import pygame as pg
import pytest

from wave_function_collapse.utils.utils_pygame import get_window_size_from_screen_resolution


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
