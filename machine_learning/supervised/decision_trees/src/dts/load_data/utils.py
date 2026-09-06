"""Module for utility functions relating to loading datasets."""

from pathlib import Path

import yaml


def load_yaml(file_path: Path) -> dict:
    """Load a YAML file and return its contents as a dictionary.

    Args:
        file_path (Path): Path to the YAML file to load.

    Returns:
        content (dict): The parsed YAML content as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the file contains invalid YAML.
    """
    try:
        with open(file_path) as file:
            content = yaml.safe_load(file)

        return content
    except FileNotFoundError as e:
        raise FileNotFoundError(f"YAML file not found: {file_path}") from e
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}") from e
