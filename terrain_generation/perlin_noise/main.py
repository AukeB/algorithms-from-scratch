"""Module for the entry point of the Perlin noise algorithm."""

from src.perlin_noise.config_manager import ConfigManager
from src.perlin_noise.perlin_noise import PerlinNoise


def main() -> None:
    """
    Orchestrate the Perlin noise algorithm from config loading through execution.
    """
    # 1. Load and validate the configuration from disk.
    config_manager = ConfigManager()
    config = config_manager.read_config()

    # 2. Generate Perlin Noise.
    pn = PerlinNoise(config=config)
    pn.generate()


if __name__ == "__main__":
    main()


"""
TODO
- Create an interactive pygame window, where you can change the way the grid looks
  based on parameter tweaking in the pygame window.
- Implement Fractar layer (octaves, persistence, fractral brownian motion)
- Simplex noise
- Domain warping
"""
