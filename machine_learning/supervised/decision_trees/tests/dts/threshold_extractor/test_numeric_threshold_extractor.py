"""Tests for the numeric_threshold_extractor module."""

import polars as pl
import pytest

from dts.threshold_extractor.numeric_threshold_extractor import (
    NumericThresholdExtractor,
)


# Testing the "__init__" method from the "NumericThresholdExtractor" class.


def test_init_stores_df_and_column_name() -> None:
    df = pl.DataFrame({"age": [25.0, 30.0]})

    extractor = NumericThresholdExtractor(df, "age")

    assert extractor.feature_column_name == "age"
    assert extractor.df is df


def test_init_raises_for_missing_column() -> None:
    df = pl.DataFrame({"age": [25.0]})

    with pytest.raises(ValueError, match="not found in dataframe"):
        NumericThresholdExtractor(df, "income")


def test_init_raises_for_non_numeric_column() -> None:
    df = pl.DataFrame({"name": ["Alice", "Bob"]})

    with pytest.raises(ValueError, match="must be numeric"):
        NumericThresholdExtractor(df, "name")


# Testing the "_get_unique_values" method from the "NumericThresholdExtractor" class.


def test_get_unique_values_returns_sorted_unique_values() -> None:
    df = pl.DataFrame({"age": [30.0, 25.0, 30.0, 40.0]})
    extractor = NumericThresholdExtractor(df, "age")

    unique_values = extractor._get_unique_values()

    assert unique_values == [25.0, 30.0, 40.0]


# Testing the "_get_split_candidates" method from the "NumericThresholdExtractor" class.


def test_get_split_candidates_returns_midpoints() -> None:
    df = pl.DataFrame({"age": [25.0, 30.0]})
    extractor = NumericThresholdExtractor(df, "age")

    candidates = extractor._get_split_candidates([25.0, 30.0, 40.0])

    assert candidates == [27.5, 35.0]


def test_get_split_candidates_is_empty_for_single_value() -> None:
    df = pl.DataFrame({"age": [25.0]})
    extractor = NumericThresholdExtractor(df, "age")

    candidates = extractor._get_split_candidates([25.0])

    assert candidates == []


# Testing the "extract" method from the "NumericThresholdExtractor" class.


def test_extract_works_for_integer_columns() -> None:
    df = pl.DataFrame({"count": [1, 2, 3]})
    extractor = NumericThresholdExtractor(df, "count")

    thresholds = extractor.extract()

    assert thresholds == [1.5, 2.5]
