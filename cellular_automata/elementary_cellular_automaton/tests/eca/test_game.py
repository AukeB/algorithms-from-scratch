"""Tests for the game module."""

from typing import Any

import pygame as pg
import pytest

from eca.config.config_model import ConfigModel
from eca.game import Game


@pytest.fixture
def game(config_data: dict[str, Any]) -> Game:
    """Provides a Game backed by the dummy pygame display.

    Args:
        config_data (dict[str, Any]): Raw configuration used to build the game.

    Returns:
        game (Game): A game ready to handle events and run.
    """
    config = ConfigModel(**config_data)

    game = Game(config=config)

    return game


# Testing the "_handle_events" method from the "Game" class.


def test_handle_events_stops_on_quit(game: Game) -> None:
    pg.event.post(pg.event.Event(pg.QUIT))

    game._handle_events()

    assert game._running is False


def test_handle_events_stops_on_escape(game: Game) -> None:
    pg.event.post(pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE))

    game._handle_events()

    assert game._running is False


# Testing the "_update" method from the "Game" class.


def test_update_propagates_grid(game: Game) -> None:
    game._update(dt=0.1)

    assert game._grid._iteration == 1


def test_update_stops_propagating_when_grid_is_full(game: Game) -> None:
    game._grid._iteration = game._grid.dimensions.rows - 1
    last_row = list(game._grid.grid[-1])

    game._update(dt=0.1)

    assert game._grid._iteration == game._grid.dimensions.rows - 1
    assert game._grid.grid[-1] == last_row


# Testing the "run" method from the "Game" class.


def test_run_exits_process_after_quit_event(game: Game) -> None:
    pg.event.post(pg.event.Event(pg.QUIT))

    with pytest.raises(SystemExit):
        game.run()
