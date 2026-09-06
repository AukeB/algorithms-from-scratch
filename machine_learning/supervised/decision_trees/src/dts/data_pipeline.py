"""Module for data loading and preprocessing pipeline."""

from polars import DataFrame

from src.dts.gini_impurity.gini_impurity_evaluator import GiniImpurityEvaluator
from src.dts.load_data.load_data import get_dataset_config, load_data
from src.dts.preprocess_data import DataPreprocessor
from src.dts.threshold_extractor.numeric_threshold_extractor import (
    NumericThresholdExtractor,
)


class DataPipeline:
    """Orchestrate the complete data loading and preprocessing pipeline.

    Manages the flow from raw data loading through preprocessing and feature
    analysis for decision tree training.

    Attributes:
        dataset (str): The dataset identifier.
        df (DataFrame): The dataframe being processed.

    Example:
        >>> pipeline = DataPipeline("iris")
        >>> df = pipeline.run()
    """

    def __init__(self, dataset: str) -> None:
        """Initialize the data pipeline.

        Loads the raw dataset from source.

        Args:
            dataset (str): The dataset identifier (e.g., 'iris', 'wine').
        """
        self.dataset: str = dataset
        self.df: DataFrame = load_data(dataset)

    def _preprocess(self) -> None:
        """Apply preprocessing operations to the dataframe."""
        preprocessor = DataPreprocessor(self.df)
        self.df = preprocessor.preprocess()

    def _evaluate_split_candidates(self) -> None:
        """Evaluate split candidate thresholds using Gini impurity for each
        numeric feature.

        Generates midpoint thresholds between consecutive unique values,
        evaluates Gini impurity for each threshold, and displays results.
        Currently only supports numeric features; categorical features will be
        handled in future iterations.
        """
        dataset_config = get_dataset_config(self.dataset)
        target_column_name = dataset_config["target"]

        for col_name in dataset_config["features"]:
            print(f"\n{'=' * 60}")
            print(f"Feature: {col_name}")
            print(f"{'=' * 60}")

            # Extract split candidates
            extractor = NumericThresholdExtractor(self.df, col_name)
            thresholds = extractor.extract()

            # Evaluate Gini impurity for each threshold
            evaluator = GiniImpurityEvaluator(
                self.df, col_name, target_column_name, thresholds
            )
            evaluator.evaluate_all_thresholds()

            # Print results for each threshold
            for threshold, metrics in evaluator.results.items():
                print(
                    f"\nThreshold: {threshold:.4f} | "
                    f"Weighted Gini: {metrics['weighted_gini']:.4f} | "
                    f"n_left: {metrics['n_left']} | "
                    f"n_right: {metrics['n_right']}"
                )

            # Print best threshold
            best_threshold = evaluator.get_best_threshold()
            print(
                f"\n>>> Best threshold: {best_threshold:.4f} "
                f"(Gini: {evaluator.results[best_threshold]['weighted_gini']:.4f})"
            )

    def run(self) -> DataFrame:
        """Execute the complete data pipeline.

        Orchestrates all pipeline steps in sequence: preprocessing and split
        candidate evaluation.

        Returns:
            df (DataFrame): The loaded and preprocessed dataframe.
        """
        self._preprocess()
        self._evaluate_split_candidates()

        return self.df
