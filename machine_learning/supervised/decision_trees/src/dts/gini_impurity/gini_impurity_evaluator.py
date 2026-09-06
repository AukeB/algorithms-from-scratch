"""Module for evaluating Gini impurity across all candidate thresholds."""

from polars import DataFrame

from src.dts.gini_impurity.single_threshold_evaluator import (
    SingleThresholdGiniEvaluator,
)


class GiniImpurityEvaluator:
    """Evaluate split quality using Gini impurity across all candidate
    thresholds.

    Iterates through candidate thresholds, evaluates each using
    SingleThresholdGiniEvaluator, and determines the best split based on
    weighted Gini impurity.

    Attributes:
        df (DataFrame): The dataframe containing features and target.
        feature_column_name (str): Name of the numeric feature column.
        target_column_name (str): Name of the target column (class labels).
        threshold_values (list[float]): Candidate split thresholds to evaluate.
        results (dict): Stores Gini metrics for each threshold.

    Example:
        >>> evaluator = GiniImpurityEvaluator(df, "age", "species", [27.5, 32.5, 37.5])
        >>> evaluator.evaluate_all_thresholds()
        >>> best_threshold = evaluator.get_best_threshold()
    """

    def __init__(
        self,
        df: DataFrame,
        feature_column_name: str,
        target_column_name: str,
        threshold_values: list[float],
    ) -> None:
        """Initialize the Gini impurity evaluator.

        Args:
            df (DataFrame): The dataframe containing features and target.
            feature_column_name (str): Name of the numeric feature column.
            target_column_name (str): Name of the target column (class labels).
            threshold_values (list[float]): Candidate split thresholds.
        """
        self.df = df
        self.feature_column_name = feature_column_name
        self.target_column_name = target_column_name
        self.threshold_values = threshold_values

        # Initialize results dict with structure for each threshold
        self.results: dict = {
            threshold: {
                "gini_left": None,
                "gini_right": None,
                "n_left": None,
                "n_right": None,
                "weighted_gini": None,
            }
            for threshold in threshold_values
        }

    def evaluate_all_thresholds(self) -> None:
        """Evaluate all candidate thresholds.

        Iterates through all threshold values, delegating each evaluation to
        SingleThresholdGiniEvaluator.
        """
        for threshold in self.threshold_values:
            single_evaluator = SingleThresholdGiniEvaluator(
                self.df,
                self.feature_column_name,
                self.target_column_name,
                threshold,
            )
            self.results[threshold] = single_evaluator.evaluate()

    def get_best_threshold(self) -> float:
        """Find the threshold with the lowest weighted Gini impurity.

        Returns:
            best_threshold (float): The threshold value with best split quality.

        Raises:
            ValueError: If results dict is empty or contains no valid splits.
        """
        if not self.results:
            raise ValueError(
                "No thresholds evaluated. Call evaluate_all_thresholds() first."
            )

        best_threshold = min(
            self.results.keys(),
            key=lambda t: self.results[t]["weighted_gini"],
        )

        return best_threshold
