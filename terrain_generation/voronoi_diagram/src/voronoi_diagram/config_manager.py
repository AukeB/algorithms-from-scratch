"""Module for loading and validating the Voronoi diagram configuration file."""

from pathlib import Path

import yaml

from voronoi_diagram.config_model import ConfigModel
from voronoi_diagram.constants import CONFIG_PATH


class ConfigManager:
    """Load and validate the config file into a ConfigModel.

    Attributes:
        config_path (Path): Path to the YAML configuration file.

    Example:
        >>> config = ConfigManager().load_config_file()
        >>> config.voronoi.num_seeds
        20
    """

    def __init__(self, config_path: Path = CONFIG_PATH) -> None:
        """Initialize the ConfigManager with a path to the config file.

        Args:
            config_path (Path): Path to the YAML configuration file to load.
        """
        self.config_path = config_path

    def load_config_file(self) -> ConfigModel:
        """Read the YAML config file and validate it into a ConfigModel.

        Returns:
            config (ConfigModel): The validated configuration.
        """
        with open(self.config_path, encoding="utf-8") as file:
            raw_config = yaml.safe_load(file)

        config = ConfigModel.model_validate(raw_config)

        return config
