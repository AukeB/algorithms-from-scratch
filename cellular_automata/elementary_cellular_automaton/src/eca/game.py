"""Module for game logic and orchestration of the main loop."""

import sys

import pygame as pg

from src.eca.config_model import ConfigModel
from src.eca.grid import Grid
from src.eca.renderer import Renderer


class Game:
    """Manages game state and orchestrates the main loop."""

    def __init__(self, config: ConfigModel) -> None:
        """Initializes the game with configuration and state.

        Args:
            config (ConfigModel): Pydantic-validated configuration model.
        """
        self.fps = config.game.fps

        self.running: bool = True

        self.grid = Grid(config=config)
        self.renderer = Renderer(config=config)

        # Random initialization for demonstration purposes.
        self.grid.randomize()

    def _handle_events(self) -> None:
        """Processes pending pygame events, including quit and key presses."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.running = False

    def _update(self, dt: float) -> None:
        """Advances game state for the current frame.

        Args:
            dt (float): Time in seconds elapsed since the last frame.
        """

    def _loop(self) -> None:
        """Runs the main loop: handle input, update state, render frame."""
        while self.running:
            dt = self.renderer.tick(self.fps)

            self._handle_events()
            self._update(dt)

            self.renderer.render(self.grid)

    def _quit(self) -> None:
        """Shuts down the renderer and exits the process cleanly."""
        self.renderer.quit()
        sys.exit()

    def run(self) -> None:
        """Orchestrates setup, main loop, and clean shutdown.

        1. Run the main loop until the game stops running.
        2. Shut down pygame and exit the process cleanly.
        """
        self._loop()
        self._quit()
