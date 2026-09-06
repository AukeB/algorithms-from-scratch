"""Module for data preprocessing operations."""

from polars import DataFrame


class DataPreprocessor:
    """Apply preprocessing operations to a dataframe.

    Orchestrates a pipeline of preprocessing steps to clean and prepare data for
    model training. Steps are applied sequentially.

    Attributes:
        df (DataFrame): The dataframe to preprocess.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({
        ...     "age": [25.0, 30.0, None, 40.0],
        ...     "name": ["Alice", "Bob", "Charlie", "David"]
        ... })
        >>> preprocessor = DataPreprocessor(df)
        >>> cleaned_df = preprocessor.preprocess()
        >>> print(cleaned_df)
    """

    def __init__(self, df: DataFrame) -> None:
        """Initialize the data preprocessor.

        Args:
            df (DataFrame): The raw dataframe to preprocess.
        """
        self.df = df

    def _remove_null_rows(self) -> None:
        """Remove rows containing any null values.

        Mutates self.df in place by dropping all rows with null values.
        """
        self.df = self.df.drop_nulls()

    def preprocess(self) -> DataFrame:
        """Apply preprocessing operations to the dataframe.

        Orchestrates a pipeline of preprocessing steps to clean and prepare data
        for model training. Steps are applied sequentially.

        Returns:
            df_processed (DataFrame): The preprocessed dataframe.
        """
        self._remove_null_rows()

        return self.df
