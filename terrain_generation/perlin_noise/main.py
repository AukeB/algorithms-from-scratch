"""Entry point for the Perlin noise visualization."""

import logging

from perlin_noise.config_manager import ConfigManager
from perlin_noise.perlin_noise import PerlinNoise


def main() -> None:
    """Load the configuration, generate the Perlin noise, and show it until the window closes."""
    logging.basicConfig(level=logging.INFO)

    config = ConfigManager().read_config()
    pn = PerlinNoise(config=config)
    pn.run()


if __name__ == "__main__":
    main()
