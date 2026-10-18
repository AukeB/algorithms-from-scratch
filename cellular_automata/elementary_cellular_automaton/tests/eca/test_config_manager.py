"""Tests for the config_manager module."""

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from eca.config.config_model import ConfigModel
from eca.config_manager import ConfigManager
from eca.constants import CONFIG_PATH


# Testing the "__init__" method from the "ConfigManager" class.


def test_init_defaults_to_project_config_path() -> None:
    config_manager = ConfigManager()

    assert config_manager.config_path == CONFIG_PATH
    assert config_manager.config_path.exists()


def test_init_accepts_custom_config_path(tmp_path: Path) -> None:
    config_path = tmp_path / "custom.yaml"

    config_manager = ConfigManager(config_path=config_path)

    assert config_manager.config_path == config_path


# Testing the "load_config_file" method from the "ConfigManager" class.


def test_load_config_file_loads_project_config() -> None:
    config_manager = ConfigManager()

    config = config_manager.load_config_file()

    assert isinstance(config, ConfigModel)
    assert config.grid.dim == 401


def test_load_config_file_parses_valid_yaml(
    tmp_path: Path, config_data: dict[str, Any]
) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config_data))
    config_manager = ConfigManager(config_path=config_path)

    config = config_manager.load_config_file()

    assert config.game.rule_set == 90
    assert config.window.caption == "Test"


def test_load_config_file_rejects_unknown_keys(
    tmp_path: Path, config_data: dict[str, Any]
) -> None:
    config_data["game"]["unknown_key"] = 1
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config_data))
    config_manager = ConfigManager(config_path=config_path)

    with pytest.raises(ValidationError):
        config_manager.load_config_file()
