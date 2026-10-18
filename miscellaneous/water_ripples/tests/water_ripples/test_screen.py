"""Tests for the screen module."""

import pygame as pg
import pytest

import water_ripples.screen as screen_module
from water_ripples.screen import resolve_window_and_grid, window_size_from_screen


# Testing the "window_size_from_screen" function.


def test_window_size_from_screen_scales_desktop_size(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(1920, 1080)])

    window_size = window_size_from_screen()

    assert window_size == (1632, 918)


def test_window_size_from_screen_clamps_to_minimum(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(100, 100)])

    window_size = window_size_from_screen()

    assert window_size == (400, 300)


def test_window_size_from_screen_initializes_display_when_needed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initialized: list[bool] = []
    monkeypatch.setattr(pg.display, "get_init", lambda: False)
    monkeypatch.setattr(pg.display, "init", lambda: initialized.append(True))
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(1920, 1080)])

    window_size_from_screen()

    assert initialized == [True]


# Testing the "resolve_window_and_grid" function.


def test_resolve_uses_screen_size_when_window_is_automatic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screen_module, "window_size_from_screen", lambda: (800, 600))

    resolved = resolve_window_and_grid(
        window_width=None,
        window_height=None,
        number_of_columns=16,
        number_of_rows=None,
    )

    assert resolved == (800, 600, 12)


def test_resolve_derives_rows_from_aspect_ratio() -> None:
    resolved = resolve_window_and_grid(
        window_width=320,
        window_height=200,
        number_of_columns=16,
        number_of_rows=None,
    )

    assert resolved == (320, 200, 10)


def test_resolve_keeps_given_rows() -> None:
    resolved = resolve_window_and_grid(
        window_width=320,
        window_height=200,
        number_of_columns=16,
        number_of_rows=7,
    )

    assert resolved == (320, 200, 7)


def test_resolve_raises_when_only_one_size_is_given() -> None:
    with pytest.raises(ValueError, match="both be None"):
        resolve_window_and_grid(
            window_width=320,
            window_height=None,
            number_of_columns=16,
            number_of_rows=None,
        )
