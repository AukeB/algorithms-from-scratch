"""Entry point for the water ripples simulation. The variant comes from the configuration file."""

import logging

from water_ripples.config_manager import ConfigManager
from water_ripples.launcher import create_simulation


def main() -> None:
    """Load the configuration, create the variant it names, and run it until the window closes."""
    logging.basicConfig(level=logging.INFO)

    config = ConfigManager().load_config_file()
    simulation = create_simulation(config=config)
    simulation.execute()


if __name__ == "__main__":
    main()
