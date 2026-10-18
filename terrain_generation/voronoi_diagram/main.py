"""Entry point for the Voronoi diagram game."""

import logging

from voronoi_diagram.config_manager import ConfigManager
from voronoi_diagram.game import Game


def main() -> None:
    """Load the configuration and run the game window until it is closed."""
    logging.basicConfig(level=logging.INFO)

    config_manager = ConfigManager()
    config = config_manager.load_config_file()

    game = Game(config=config)
    game.run()


if __name__ == "__main__":
    main()
