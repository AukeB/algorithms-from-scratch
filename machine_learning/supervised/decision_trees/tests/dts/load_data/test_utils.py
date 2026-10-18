"""Tests for the load_data utils module."""

from pathlib import Path

import pytest
import yaml

from dts.load_data.utils import load_yaml


# Testing the "load_yaml" function.


def test_load_yaml_returns_parsed_content(tmp_path: Path) -> None:
    file_path = tmp_path / "config.yaml"
    file_path.write_text("iris:\n  target: species\n")

    content = load_yaml(file_path)

    assert content == {"iris": {"target": "species"}}


def test_load_yaml_raises_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="YAML file not found"):
        load_yaml(tmp_path / "missing.yaml")


def test_load_yaml_raises_for_invalid_yaml(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.yaml"
    file_path.write_text("key: [unclosed\n")

    with pytest.raises(yaml.YAMLError, match="Invalid YAML"):
        load_yaml(file_path)
