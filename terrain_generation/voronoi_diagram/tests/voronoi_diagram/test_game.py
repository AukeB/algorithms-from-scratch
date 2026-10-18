"""Tests for the game module."""

import pygame as pg

from voronoi_diagram.config_model import ConfigModel
from voronoi_diagram.game import Game
from typing import Callable


# Testing the "__init__" method from the "Game" class.


def test_init_computes_the_voronoi_diagram_once(small_config: ConfigModel) -> None:
    game = Game(config=small_config)

    assert len(game.grid.seed_points) == 4
    assert all(
        0 <= owner < 4 for row in game.grid.cells for owner in row
    )


# Testing the "_handle_events" method from the "Game" class.


def test_handle_events_keeps_running_for_other_keys(
    small_config: ConfigModel, scripted_input: Callable[..., None]
) -> None:
    game = Game(config=small_config)
    scripted_input(event_batches=[[pg.event.Event(pg.KEYDOWN, key=pg.K_a)]])

    game._handle_events()

    assert game.running is True


def test_handle_events_stops_on_escape(
    small_config: ConfigModel, scripted_input: Callable[..., None]
) -> None:
    game = Game(config=small_config)
    scripted_input(event_batches=[[pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE)]])

    game._handle_events()

    assert game.running is False


def test_handle_events_stops_on_window_close(
    small_config: ConfigModel, scripted_input: Callable[..., None]
) -> None:
    game = Game(config=small_config)
    scripted_input(event_batches=[[pg.event.Event(pg.QUIT)]])

    game._handle_events()

    assert game.running is False


# Testing the "run" method from the "Game" class.


def test_run_renders_until_the_window_closes(
    small_config: ConfigModel, scripted_input: Callable[..., None]
) -> None:
    game = Game(config=small_config)
    scripted_input(event_batches=[[], [pg.event.Event(pg.QUIT)]])

    game.run()

    assert game.running is False
    assert not pg.display.get_init()
