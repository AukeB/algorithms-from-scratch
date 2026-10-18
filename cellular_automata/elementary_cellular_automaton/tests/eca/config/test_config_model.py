"""Tests for the config_model module."""

from typing import Any

import pytest
from pydantic import ValidationError

from eca.config.config_model import ConfigModel


# Testing the "ConfigModel" class.


def test_config_model_accepts_valid_config(config_data: dict[str, Any]) -> None:
    config = ConfigModel(**config_data)

    assert config.game.fps == 10
    assert config.grid.dim == 5


def test_config_model_rejects_unknown_keys(config_data: dict[str, Any]) -> None:
    config_data["window"]["unknown_key"] = 1

    with pytest.raises(ValidationError):
        ConfigModel(**config_data)


# Testing the "rule_set" field from the "ConfigGame" class.


@pytest.mark.parametrize("rule_set", [0, 255])
def test_rule_set_accepts_bounds(config_data: dict[str, Any], rule_set: int) -> None:
    config_data["game"]["rule_set"] = rule_set

    config = ConfigModel(**config_data)

    assert config.game.rule_set == rule_set


@pytest.mark.parametrize("rule_set", [-1, 256])
def test_rule_set_rejects_out_of_range(config_data: dict[str, Any], rule_set: int) -> None:
    config_data["game"]["rule_set"] = rule_set

    with pytest.raises(ValidationError):
        ConfigModel(**config_data)


# Testing the "_validate_dim_is_odd" method from the "ConfigGrid" class.


def test_validate_dim_is_odd_accepts_odd_dim(config_data: dict[str, Any]) -> None:
    config_data["grid"]["dim"] = 7

    config = ConfigModel(**config_data)

    assert config.grid.dim == 7


def test_validate_dim_is_odd_rejects_even_dim(config_data: dict[str, Any]) -> None:
    config_data["grid"]["dim"] = 4

    with pytest.raises(ValidationError, match="must be odd"):
        ConfigModel(**config_data)
