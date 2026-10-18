"""Module for running the main repository workflow."""

import logging

from eca.config_manager import ConfigManager
from eca.game import Game


def main() -> None:
    """Configures logging, loads configuration, and launches the pygame window."""
    logging.basicConfig(level=logging.INFO)

    config_manager = ConfigManager()
    config = config_manager.load_config_file()

    game = Game(config=config)
    game.run()


if __name__ == "__main__":
    main()
