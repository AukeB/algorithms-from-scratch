"""Tests for the preprocess_data module."""

import polars as pl

from dts.preprocess_data import DataPreprocessor


# Testing the "preprocess" method from the "DataPreprocessor" class.


def test_preprocess_drops_rows_with_null_values() -> None:
    df = pl.DataFrame({"age": [25.0, None, 40.0], "name": ["Alice", "Bob", "David"]})
    preprocessor = DataPreprocessor(df)

    df_processed = preprocessor.preprocess()

    assert df_processed["name"].to_list() == ["Alice", "David"]
