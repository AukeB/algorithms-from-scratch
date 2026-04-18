"""Module for loading and validating the WFC configuration file."""

import yaml

from src.wave_function_collapse.config_model import ConfigModel
from src.wave_function_collapse.constants import CONFIG_FILE_PATH


class ConfigManager:
    """Loads and validates config.yaml into a ConfigModel instance."""

    def __init__(self) -> None:
        """Store the path to the config file for later reading."""
        self.config_file_path = CONFIG_FILE_PATH

    def read_config(self) -> ConfigModel:
        """
        Read, validate, and return the config file as a ConfigModel instance.

        1. Verify the config file exists on disk.
        2. Parse it with yaml.safe_load.
        3. Validate the parsed dict against ConfigModel.
        4. Return the validated config as a ConfigModel instance.

        Returns:
            config (ConfigModel): The validated configuration model.

        Raises:
            FileNotFoundError: If the config file path does not exist on disk.
        """
        if not self.config_file_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file_path}")

        with open(self.config_file_path, "r", encoding="utf-8") as file:
            raw = yaml.safe_load(file)

        config = ConfigModel(**raw)

        return config
