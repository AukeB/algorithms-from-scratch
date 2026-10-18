"""Tests for the data_loader module."""

import logging
from pathlib import Path

import pytest

from gpt_tokenizer.data_loader import DataLoader


# Testing the "load_text" method from the "DataLoader" class.


def test_load_text_returns_file_contents(tmp_path: Path) -> None:
    file_path = tmp_path / "text.txt"
    file_path.write_text("Hello  world\n", encoding="utf-8")
    data_loader = DataLoader(str(file_path))

    text = data_loader.load_text()

    assert text == "Hello  world\n"


def test_load_text_returns_empty_string_for_missing_file(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    data_loader = DataLoader(str(tmp_path / "missing.txt"))

    with caplog.at_level(logging.ERROR, logger="gpt_tokenizer.data_loader"):
        text = data_loader.load_text()

    assert text == ""
    assert "not found" in caplog.text


def test_load_text_returns_empty_string_for_other_errors(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    # Opening a directory raises IsADirectoryError, which is not FileNotFoundError.
    data_loader = DataLoader(str(tmp_path))

    with caplog.at_level(logging.ERROR, logger="gpt_tokenizer.data_loader"):
        text = data_loader.load_text()

    assert text == ""
    assert "Error:" in caplog.text


# Testing the "clean_text" method from the "DataLoader" class.


def test_clean_text_collapses_spaces_and_newlines_and_strips() -> None:
    data_loader = DataLoader("unused.txt")

    cleaned_text = data_loader.clean_text("  Hello    world\n\n\nagain  \n")

    assert cleaned_text == "Hello world\nagain"
