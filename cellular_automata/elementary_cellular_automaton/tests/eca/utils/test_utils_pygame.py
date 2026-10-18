"""Tests for the utils_pygame module."""

from types import SimpleNamespace

import pygame as pg
import pytest

from eca.utils.utils_pygame import get_window_size_from_screen_resolution


# Testing the "get_window_size_from_screen_resolution" function.


def test_window_size_is_fraction_of_desktop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pg.display, "get_init", lambda: True)
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(1920, 1080)])

    window_size = get_window_size_from_screen_resolution()

    assert window_size == (1728, 972)


def test_window_size_is_clamped_to_minimum(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pg.display, "get_init", lambda: True)
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(500, 400)])

    window_size = get_window_size_from_screen_resolution()

    assert window_size == (450, 360)


def test_window_size_initializes_display_when_inactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_calls: list[str] = []
    monkeypatch.setattr(pg.display, "get_init", lambda: False)
    monkeypatch.setattr(pg.display, "init", lambda: init_calls.append("init"))
    monkeypatch.setattr(pg.display, "get_desktop_sizes", lambda: [(1920, 1080)])

    get_window_size_from_screen_resolution()

    assert init_calls == ["init"]


def test_window_size_uses_legacy_display_info_for_old_pygame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    info = SimpleNamespace(current_w=1600, current_h=900)
    monkeypatch.setattr(pg.display, "get_init", lambda: True)
    monkeypatch.setattr(pg.version, "vernum", (1, 9, 6))
    monkeypatch.setattr(pg.display, "Info", lambda: info)

    window_size = get_window_size_from_screen_resolution()

    assert window_size == (1440, 810)


def test_window_size_falls_back_to_1080p_for_legacy_pygame_without_info(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    info = SimpleNamespace(current_w=0, current_h=0)
    monkeypatch.setattr(pg.display, "get_init", lambda: True)
    monkeypatch.setattr(pg.version, "vernum", (1, 9, 6))
    monkeypatch.setattr(pg.display, "Info", lambda: info)

    window_size = get_window_size_from_screen_resolution()

    assert window_size == (1728, 972)
