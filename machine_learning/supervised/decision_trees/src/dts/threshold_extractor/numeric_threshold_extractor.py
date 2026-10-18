"""Module for extracting split candidate thresholds from numeric features.

Provides utilities for decision tree node evaluation. Extracts unique values
from numeric feature columns and generates split candidate thresholds (midpoints
between consecutive values). These thresholds serve as potential split points
when evaluating Gini impurity or other split criteria during tree construction.

Classes: NumericThresholdExtractor: Extract unique values and generate split
candidates in one call.

Example:
    >>> from dts.threshold_extractor.numeric_threshold_extractor import NumericThresholdExtractor
    >>> extractor = NumericThresholdExtractor(df, "age")
    >>> thresholds = extractor.extract()
"""

from itertools import pairwise

import polars as pl
from polars import DataFrame

_NUMERIC_DTYPES: tuple[type[pl.DataType], ...] = (
    pl.Float32,
    pl.Float64,
    pl.Int8,
    pl.Int16,
    pl.Int32,
    pl.Int64,
)


class NumericThresholdExtractor:
    """Extract and generate split candidate thresholds from a numeric feature
    column.

    This class encapsulates the logic for extracting unique values from a
    numeric feature and generating split candidate thresholds (midpoints between
    consecutive values) for decision tree node evaluation.

    Attributes:
        df (DataFrame): The dataframe containing the feature column.
        feature_column_name (str): Name of the numeric feature column.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({
        ...     "age": [25.0, 30.0, 35.0, 40.0, 45.0],
        ...     "income": [50000, 60000, 70000, 80000, 90000]
        ... })
        >>> extractor = NumericThresholdExtractor(df, "age")
        >>> thresholds = extractor.extract()
        >>> print(thresholds)
        [27.5, 32.5, 37.5, 42.5]
    """

    def __init__(self, df: DataFrame, feature_column_name: str) -> None:
        """Initialize the numeric threshold extractor.

        Args:
            df (DataFrame): The dataframe containing the feature column.
            feature_column_name (str): Name of the numeric feature column.

        Raises:
            ValueError: If the column does not exist or is not numeric.
        """
        self._validate_column(df, feature_column_name)

        self.df = df
        self.feature_column_name = feature_column_name

    def _validate_column(self, df: DataFrame, feature_column_name: str) -> None:
        """Validate that the feature column exists and is numeric.

        Args:
            df (DataFrame): The dataframe to validate.
            feature_column_name (str): Name of the column to validate.

        Raises:
            ValueError: If column does not exist or is not numeric.
        """
        if feature_column_name not in df.columns:
            raise ValueError(f"Column '{feature_column_name}' not found in dataframe")

        col_dtype = df[feature_column_name].dtype

        if col_dtype not in _NUMERIC_DTYPES:
            raise ValueError(
                f"Column '{feature_column_name}' must be numeric, got {col_dtype}"
            )

    def _get_unique_values(self) -> list[float]:
        """Extract unique values from the feature column.

        Returns:
            unique_values (list[float]): Sorted list of unique values.
        """
        unique_values = self.df[self.feature_column_name].unique().sort().to_list()

        return unique_values

    def _get_split_candidates(self, unique_values: list[float]) -> list[float]:
        """Generate split candidate thresholds from unique values.

        Creates midpoints between consecutive unique values, which serve as
        candidate thresholds for splitting in decision tree node evaluation.

        Args:
            unique_values (list[float]): Sorted list of unique numeric values.

        Returns:
            candidates (list[float]): Midpoints between consecutive values.
        """
        candidates: list[float] = []

        for lower_value, upper_value in pairwise(unique_values):
            midpoint = round((lower_value + upper_value) / 2, 10)
            candidates.append(midpoint)

        return candidates

    def extract(self) -> list[float]:
        """Extract and generate split candidate thresholds in a single call.

        Returns:
            candidates (list[float]): Split candidate thresholds.
        """
        unique_values = self._get_unique_values()
        candidates = self._get_split_candidates(unique_values)

        return candidates
