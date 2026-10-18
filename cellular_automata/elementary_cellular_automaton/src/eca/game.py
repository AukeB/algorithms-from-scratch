"""Module for game logic and orchestration of the main loop."""

import sys

import pygame as pg

from eca.config.config_model import ConfigModel
from eca.grid import Grid
from eca.renderer import Renderer


class Game:
    """Manages game state and orchestrates the main loop.

    Attributes:
        _fps (int): Target frames per second.
        _running (bool): Whether the main loop keeps running.
        _grid (Grid): The cell grid that is propagated each frame.
        _renderer (Renderer): Draws the grid to the pygame window.

    Example:
        config = ConfigManager().load_config_file() game = Game(config=config)
        game.run()
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initializes the game with configuration and state.

        Args:
            config (ConfigModel): Pydantic-validated configuration model.
        """
        self._fps: int = config.game.fps

        self._running: bool = True

        self._grid = Grid(config=config)
        self._renderer = Renderer(config=config)

        self._grid.initialize()

    def _handle_events(self) -> None:
        """Processes pending pygame events, including quit and key presses."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._running = False

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self._running = False

    def _update(self, dt: float) -> None:
        """Advances game state for the current frame.

        Once the grid is full, the simulation stops and the last frame stays on
        screen until the window is closed.

        Args:
            dt (float): Time in seconds elapsed since the last frame.
        """
        if not self._grid.is_full:
            self._grid.propagate()

    def _loop(self) -> None:
        """Runs the main loop: handle input, update state, render frame."""
        while self._running:
            dt = self._renderer.tick(self._fps)

            self._handle_events()
            self._update(dt)

            self._renderer.render(self._grid)

    def _quit(self) -> None:
        """Shuts down the renderer and exits the process cleanly."""
        self._renderer.quit()
        sys.exit()

    def run(self) -> None:
        """Orchestrates setup, main loop, and clean shutdown.

        1. Run the main loop until the game stops running.
        2. Shut down pygame and exit the process cleanly.
        """
        self._loop()
        self._quit()
