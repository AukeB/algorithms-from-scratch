"""Module for running the main repository workflow."""

from src.eca.config_manager import ConfigManager
from src.eca.game import Game


def main() -> None:
    """Loads configuration and launches the pygame game window."""
    config_manager = ConfigManager()
    config = config_manager.load_config_file()

    game = Game(config=config)
    game.run()


if __name__ == "__main__":
    main()
