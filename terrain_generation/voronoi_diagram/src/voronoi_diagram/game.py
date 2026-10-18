"""Module for the game loop that ties the grid and the renderer together."""

import pygame as pg

from voronoi_diagram.config_model import ConfigModel
from voronoi_diagram.grid import Grid
from voronoi_diagram.renderer import Renderer


class Game:
    """Run the main loop: handle input, keep the Voronoi diagram, and render each frame.

    Attributes:
        fps (int): Target frames per second.
        running (bool): False once the window is closed or ESC is pressed.
        num_seeds (int): Number of seed points.
        grid (Grid): The grid, holding the seed points and the Voronoi cells.
        renderer (Renderer): Owns the window and draws the grid.

    Example:
        >>> game = Game(config=ConfigManager().load_config_file())
        >>> game.run()
    """

    def __init__(self, config: ConfigModel) -> None:
        """Set up the grid and the renderer, and compute the Voronoi diagram once.

        The seed points do not move, so the diagram only has to be computed once.

        Args:
            config (ConfigModel): The validated configuration model.
        """
        self.fps = config.game.fps
        self.running = True
        self.num_seeds = config.voronoi.num_seeds

        self.grid = Grid(config=config)
        self.renderer = Renderer(config=config)

        self.grid.generate_seed_points(self.num_seeds)
        self.grid.generate_voronoi_diagram()

    def _handle_events(self) -> None:
        """Process the pending pygame events: closing the window and pressing ESC stop
        the game.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.running = False

    def _loop(self) -> None:
        """Run the main loop: cap the frame rate, handle input, and render, until the
        game stops.
        """
        while self.running:
            self.renderer.tick(self.fps)
            self._handle_events()
            self.renderer.render(self.grid)

    def run(self) -> None:
        """Run the game until it stops, then shut pygame down."""
        self._loop()
        self.renderer.quit()
