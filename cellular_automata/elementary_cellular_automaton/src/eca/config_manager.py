"""Module for loading the configuration files."""

from pathlib import Path
from typing import Any

import yaml

from eca.config.config_model import ConfigModel
from eca.constants import CONFIG_PATH


class ConfigManager:
    """Loads and validates configuration files into a ConfigModel.

    Handles reading a YAML config file from disk and parsing it into a validated
    Pydantic model.

    Attributes:
        config_path (Path): Path to the YAML configuration file to load.

    Example:
        >>> config_manager = ConfigManager()
        >>> config = config_manager.load_config_file()
    """

    def __init__(self, config_path: Path = CONFIG_PATH) -> None:
        """Initializes the ConfigManager with a path to the config file.

        Args:
            config_path (Path): Path to the YAML configuration file to load.
        """
        self.config_path: Path = config_path

    def load_config_file(self) -> ConfigModel:
        """Reads the YAML config file and parses it into a ConfigModel.

        1. Opens the config file at self.config_path.
        2. Parses the file contents as YAML.
        3. Validates and structures the parsed data into a ConfigModel.

        Returns:
            config_model (ConfigModel): The validated configuration object.
        """
        with open(self.config_path) as file:
            # The raw YAML shape is only known once Pydantic validates it below.
            config: dict[str, Any] = yaml.safe_load(file)

        config_model = ConfigModel(**config)

        return config_model
