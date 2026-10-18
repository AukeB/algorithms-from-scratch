"""Tests for the config_manager module."""

from pathlib import Path
from typing import Any, get_args

import pydantic
import pytest
import yaml

from water_ripples.config_manager import ConfigManager
from water_ripples.config_model import ConfigModel, Variant


# Testing the "load_config_file" method from the "ConfigManager" class.


def test_load_config_file_reads_default_config() -> None:
    config = ConfigManager().load_config_file()

    assert isinstance(config, ConfigModel)
    assert config.variant in get_args(Variant)
    assert config.simulation.number_of_columns == 200


def test_load_config_file_reads_custom_path(
    tmp_path: Path, config_data: dict[str, Any]
) -> None:
    config_path = tmp_path / "config.yaml"
    config_data["variant"] = "trapezoid"
    config_path.write_text(yaml.safe_dump(config_data))

    config = ConfigManager(config_path=config_path).load_config_file()

    assert config.variant == "trapezoid"
    assert config.window.window_width == 320


def test_config_rejects_unknown_variant(config_data: dict[str, Any]) -> None:
    config_data["variant"] = "pyramid"

    with pytest.raises(pydantic.ValidationError):
        ConfigModel.model_validate(config_data)


def test_config_rejects_unknown_keys(config_data: dict[str, Any]) -> None:
    config_data["simulation"]["unknown_key"] = 1

    with pytest.raises(pydantic.ValidationError):
        ConfigModel.model_validate(config_data)
