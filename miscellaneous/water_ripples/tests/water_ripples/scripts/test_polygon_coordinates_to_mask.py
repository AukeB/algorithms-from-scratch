"""Tests for the polygon_coordinates_to_mask script."""

import importlib
import importlib.util
import logging
import runpy
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from water_ripples.config_manager import ConfigManager
from water_ripples.config_model import ConfigModel

_MODULE_NAME = "water_ripples.scripts.polygon_coordinates_to_mask"


def _script_file() -> str:
    """Find the source file of the script, to run it as a script.

    Returns:
        origin (str): Path to the script's source file.
    """
    spec = importlib.util.find_spec(_MODULE_NAME)
    assert spec is not None and spec.origin is not None

    return spec.origin


# Testing the "main" function, run as the script entry point.


def test_importing_the_script_does_not_run_main(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(self: ConfigManager) -> ConfigModel:
        raise AssertionError("main must not run on import")

    monkeypatch.setattr(ConfigManager, "load_config_file", fail_if_called)

    importlib.import_module(_MODULE_NAME)


def test_main_rasterizes_polygon_into_mask_file(
    config_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    mask_path = tmp_path / "generated_mask.npy"
    config_data["image"]["mask_path"] = str(mask_path)
    config = ConfigModel.model_validate(config_data)
    monkeypatch.setattr(ConfigManager, "load_config_file", lambda self: config)

    with caplog.at_level(logging.INFO):
        runpy.run_path(_script_file(), run_name="__main__")

    mask = np.load(mask_path)
    assert mask.shape == (250, 400)
    assert mask.any()
    assert "Saved mask of shape (250, 400)" in caplog.text
