"""Module for loading the configuration file."""

from pathlib import Path

import yaml

from water_ripples.config_model import ConfigModel
from water_ripples.constants import CONFIG_PATH


class ConfigManager:
    """Load and validate the configuration file into a ConfigModel.

    Attributes:
        config_path (Path): Path to the YAML configuration file.

    Example:
        >>> config = ConfigManager().load_config_file()
        >>> config.variant
        'baseline'
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
        with open(self.config_path) as file:
            raw_config = yaml.safe_load(file)

        config = ConfigModel.model_validate(raw_config)

        return config
