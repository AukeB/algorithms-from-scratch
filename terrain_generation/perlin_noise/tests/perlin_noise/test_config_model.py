"""Tests for the config_model module."""

from typing import Any

import pydantic
import pytest

from perlin_noise.config_model import ConfigModel


# Testing the "ConfigModel" class.


def test_config_model_rejects_unknown_keys(raw_config: dict[str, Any]) -> None:
    raw_config["grid"]["unknown"] = 1

    with pytest.raises(pydantic.ValidationError):
        ConfigModel.model_validate(raw_config)


def test_config_model_rejects_unknown_smoothing_version(raw_config: dict[str, Any]) -> None:
    raw_config["grid"]["smoothing_version"] = "cubic"

    with pytest.raises(pydantic.ValidationError):
        ConfigModel.model_validate(raw_config)


def test_config_model_accepts_null_random_seed(raw_config: dict[str, Any]) -> None:
    raw_config["grid"]["random_seed"] = None

    config = ConfigModel.model_validate(raw_config)

    assert config.grid.random_seed is None
