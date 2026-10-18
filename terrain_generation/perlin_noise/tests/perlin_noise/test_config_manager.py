"""Tests for the config_manager module."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from perlin_noise.config_manager import ConfigManager
from perlin_noise.config_model import ConfigModel


# Testing the "read_config" method from the "ConfigManager" class.


def test_read_config_loads_the_default_file() -> None:
    config = ConfigManager().read_config()

    assert isinstance(config, ConfigModel)
    assert config.grid.dim == 5


def test_read_config_loads_a_custom_file(tmp_path: Path, raw_config: dict[str, Any]) -> None:
    config_file_path = tmp_path / "config.yaml"
    raw_config["grid"]["dim"] = 7
    config_file_path.write_text(yaml.safe_dump(raw_config))

    config = ConfigManager(config_file_path=config_file_path).read_config()

    assert config.grid.dim == 7


def test_read_config_raises_for_missing_file(tmp_path: Path) -> None:
    config_manager = ConfigManager(config_file_path=tmp_path / "missing.yaml")

    with pytest.raises(FileNotFoundError, match="Config file not found"):
        config_manager.read_config()
