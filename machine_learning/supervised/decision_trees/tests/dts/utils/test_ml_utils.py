"""Tests for the ml_utils module."""

import polars as pl
import pytest

from dts.utils.ml_utils import split_data


# Testing the "split_data" function.


def test_split_data_puts_values_below_threshold_left() -> None:
    df = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0], "y": ["a", "a", "b", "b"]})

    df_left, df_right = split_data(df, "x", 3.0)

    assert df_left["x"].to_list() == [1.0, 2.0]
    assert df_right["x"].to_list() == [3.0, 4.0]


def test_split_data_raises_for_missing_column() -> None:
    df = pl.DataFrame({"x": [1.0]})

    with pytest.raises(ValueError, match="not found in dataframe"):
        split_data(df, "missing", 0.5)
