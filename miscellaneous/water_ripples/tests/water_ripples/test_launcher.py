"""Tests for the launcher module."""

from typing import Any

import pytest

from water_ripples.baseline import BaselineRipples
from water_ripples.config_model import ConfigModel
from water_ripples.image_overlay import ImageRipples
from water_ripples.launcher import create_simulation
from water_ripples.trapezoid import TrapezoidRipples


# Testing the "create_simulation" function.


@pytest.mark.parametrize(
    ("variant", "expected_class"),
    [
        ("baseline", BaselineRipples),
        ("trapezoid", TrapezoidRipples),
        ("image", ImageRipples),
    ],
)
def test_create_simulation_builds_the_configured_variant(
    config_data: dict[str, Any], variant: str, expected_class: type
) -> None:
    config_data["variant"] = variant
    config = ConfigModel.model_validate(config_data)

    simulation = create_simulation(config=config)

    assert type(simulation) is expected_class
