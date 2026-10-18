"""Tests for the load_data module."""

from typing import Any

import polars as pl
import pytest

from dts.load_data.load_data import get_dataset_config, load_data


# Testing the "get_dataset_config" function.


def test_get_dataset_config_returns_known_dataset() -> None:
    dataset_config = get_dataset_config("iris")

    assert dataset_config["target"] == "species"
    assert dataset_config["features"] == [
        "sepal_length",
        "sepal_width",
        "petal_length",
        "petal_width",
    ]


def test_get_dataset_config_raises_for_unknown_dataset() -> None:
    with pytest.raises(ValueError, match="Unknown dataset: titanic"):
        get_dataset_config("titanic")


def test_wine_config_has_no_duplicate_columns() -> None:
    dataset_config = get_dataset_config("wine")
    all_columns = dataset_config["features"] + [dataset_config["target"]]

    assert len(all_columns) == len(set(all_columns)) == 14


# Testing the "load_data" function.


def test_load_data_reads_csv_with_dataset_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_read_csv(url: str, has_header: bool, new_columns: list[str]) -> pl.DataFrame:
        calls.append({"url": url, "has_header": has_header, "new_columns": new_columns})

        return pl.DataFrame()

    monkeypatch.setattr(pl, "read_csv", fake_read_csv)

    df = load_data("iris")

    assert df.is_empty()
    assert calls == [
        {
            "url": get_dataset_config("iris")["url"],
            "has_header": False,
            "new_columns": [
                "sepal_length",
                "sepal_width",
                "petal_length",
                "petal_width",
                "species",
            ],
        }
    ]


def test_load_data_raises_for_unknown_dataset() -> None:
    with pytest.raises(ValueError, match="Unknown dataset"):
        load_data("titanic")
