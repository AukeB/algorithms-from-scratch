"""Tests for the config_model module."""

from typing import Any

import pydantic
import pytest

from wave_function_collapse.config_model import ConfigModel


# Testing the "ConfigModel" class.


def test_config_model_rejects_unknown_keys(raw_config: dict[str, Any]) -> None:
    raw_config["general"]["unknown"] = 1

    with pytest.raises(pydantic.ValidationError):
        ConfigModel.model_validate(raw_config)


def test_config_model_rejects_non_positive_tile_dim(raw_config: dict[str, Any]) -> None:
    raw_config["general"]["tile_dim"] = 0

    with pytest.raises(pydantic.ValidationError):
        ConfigModel.model_validate(raw_config)


def test_config_model_rejects_unknown_mode(raw_config: dict[str, Any]) -> None:
    raw_config["modes"]["mode_model"] = "pyramid"

    with pytest.raises(pydantic.ValidationError):
        ConfigModel.model_validate(raw_config)
