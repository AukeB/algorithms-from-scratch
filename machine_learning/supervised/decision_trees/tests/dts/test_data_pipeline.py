"""Tests for the data_pipeline module."""

import logging

import polars as pl
import pytest

from dts.data_pipeline import DataPipeline


@pytest.fixture
def iris_like_df() -> pl.DataFrame:
    """Provides a small iris-shaped dataset with one row containing a null.

    Returns:
        df (pl.DataFrame): Four numeric features and a species label.
    """
    df = pl.DataFrame(
        {
            "sepal_length": [4.0, 5.0, 6.0, 7.0, None],
            "sepal_width": [3.0, 3.1, 3.2, 3.3, 3.4],
            "petal_length": [1.0, 1.1, 4.0, 4.1, 1.2],
            "petal_width": [0.2, 0.3, 1.2, 1.3, 0.1],
            "species": ["a", "a", "b", "b", "a"],
        }
    )

    return df


# Testing the "__init__" method from the "DataPipeline" class.


def test_init_loads_dataset(
    monkeypatch: pytest.MonkeyPatch, iris_like_df: pl.DataFrame
) -> None:
    monkeypatch.setattr("dts.data_pipeline.load_data", lambda dataset: iris_like_df)

    pipeline = DataPipeline("iris")

    assert pipeline.dataset == "iris"
    assert pipeline.df is iris_like_df


# Testing the "run" method from the "DataPipeline" class.


def test_run_preprocesses_and_logs_best_threshold(
    monkeypatch: pytest.MonkeyPatch,
    iris_like_df: pl.DataFrame,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr("dts.data_pipeline.load_data", lambda dataset: iris_like_df)
    pipeline = DataPipeline("iris")

    with caplog.at_level(logging.INFO, logger="dts.data_pipeline"):
        df = pipeline.run()

    assert df.height == 4
    assert "Feature: sepal_length" in caplog.text
    assert "Best threshold" in caplog.text
