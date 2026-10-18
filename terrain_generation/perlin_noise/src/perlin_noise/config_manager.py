"""Module for loading and validating the Perlin noise configuration file."""

from pathlib import Path

import yaml

from perlin_noise.config_model import ConfigModel
from perlin_noise.constants import CONFIG_FILE_PATH


class ConfigManager:
    """Load and validate the config file into a ConfigModel.

    Attributes:
        config_file_path (Path): Path to the YAML configuration file.

    Example:
        >>> config = ConfigManager().read_config()
        >>> config.grid.dim
        5
    """

    def __init__(self, config_file_path: Path = CONFIG_FILE_PATH) -> None:
        """Store the path to the config file for later reading.

        Args:
            config_file_path (Path): Path to the YAML configuration file.
        """
        self.config_file_path = config_file_path

    def read_config(self) -> ConfigModel:
        """Read, validate, and return the config file.

        Returns:
            config (ConfigModel): The validated configuration.

        Raises:
            FileNotFoundError: If the config file does not exist.
        """
        if not self.config_file_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file_path}")

        with open(self.config_file_path, encoding="utf-8") as file:
            raw_config = yaml.safe_load(file)

        config = ConfigModel.model_validate(raw_config)

        return config
