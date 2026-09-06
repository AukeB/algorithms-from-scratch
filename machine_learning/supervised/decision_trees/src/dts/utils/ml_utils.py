"""Module for machine learning utility functions."""

import polars as pl
from polars import DataFrame


def split_data(
    df: DataFrame, feature_column_name: str, threshold_value: float
) -> tuple[DataFrame, DataFrame]:
    """Split a dataframe into two groups based on a feature threshold.

    Partitions the input dataframe into left and right groups by comparing
    values in the specified feature column against the threshold value.

    Args:
        df (DataFrame): The dataframe to split.
        feature_column_name (str): Name of the feature column to split on.
        threshold_value (float): The threshold value for splitting.

    Returns:
        df_left (DataFrame): Rows where feature_column_name < threshold_value.
        df_right (DataFrame): Rows where feature_column_name >= threshold_value.
    """
    if feature_column_name not in df.columns:
        raise ValueError(f"Column '{feature_column_name}' not found in dataframe")

    df_left = df.filter(pl.col(feature_column_name) < threshold_value)
    df_right = df.filter(pl.col(feature_column_name) >= threshold_value)

    return df_left, df_right
