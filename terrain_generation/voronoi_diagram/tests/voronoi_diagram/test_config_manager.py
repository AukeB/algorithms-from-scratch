"""Tests for the config_manager module."""

from pathlib import Path

import pydantic
import pytest
import yaml

from voronoi_diagram.config_manager import ConfigManager
from voronoi_diagram.config_model import ConfigModel


# Testing the "load_config_file" method from the "ConfigManager" class.


def test_load_config_file_reads_the_default_file() -> None:
    config = ConfigManager().load_config_file()

    assert isinstance(config, ConfigModel)
    assert config.voronoi.num_seeds == 20


def test_load_config_file_reads_a_custom_file(tmp_path: Path, raw_config: dict) -> None:
    config_path = tmp_path / "config.yaml"
    raw_config["grid"]["dim"] = 12
    config_path.write_text(yaml.safe_dump(raw_config))

    config = ConfigManager(config_path=config_path).load_config_file()

    assert config.grid.dim == 12


def test_load_config_file_rejects_unknown_keys(tmp_path: Path, raw_config: dict) -> None:
    config_path = tmp_path / "config.yaml"
    raw_config["grid"]["unknown"] = True
    config_path.write_text(yaml.safe_dump(raw_config))

    with pytest.raises(pydantic.ValidationError):
        ConfigManager(config_path=config_path).load_config_file()
