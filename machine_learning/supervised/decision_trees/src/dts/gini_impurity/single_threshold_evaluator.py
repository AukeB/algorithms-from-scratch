"""Module for evaluating Gini impurity of a single threshold split."""

from polars import DataFrame

from src.dts.metrics.impurity_metrics import compute_gini, compute_weighted_gini
from src.dts.utils.ml_utils import split_data


class SingleThresholdGiniEvaluator:
    """Evaluate Gini impurity for a single candidate threshold.

    Splits data at a given threshold and computes weighted Gini impurity for the
    resulting left and right groups.

    Attributes:
        df (DataFrame): The dataframe containing features and target.
        feature_column_name (str): Name of the numeric feature column.
        target_column_name (str): Name of the target column (class labels).
        threshold (float): The threshold value to evaluate.

    Example:
        >>> evaluator = SingleThresholdGiniEvaluator(df, "age", "species", 32.5, n_total=150)
        >>> result = evaluator.evaluate()
    """

    def __init__(
        self,
        df: DataFrame,
        feature_column_name: str,
        target_column_name: str,
        threshold: float,
    ) -> None:
        """Initialize the single threshold evaluator.

        Args:
            df (DataFrame): The dataframe containing features and target.
            feature_column_name (str): Name of the numeric feature column.
            target_column_name (str): Name of the target column (class labels).
            threshold (float): The threshold value to evaluate.
        """
        self.df = df
        self.feature_column_name = feature_column_name
        self.target_column_name = target_column_name
        self.threshold = threshold

    def evaluate(self) -> dict:
        """Evaluate the Gini impurity split at this threshold.

        Splits data into left and right groups, computes Gini for each, and
        calculates weighted Gini.

        Returns:
            result (dict): Contains gini_left, gini_right, n_left, n_right, and
                weighted_gini for this threshold.
        """
        # Split data
        df_left, df_right = split_data(
            self.df, self.feature_column_name, self.threshold
        )

        # Get target labels for each group
        left_target_labels = df_left[self.target_column_name].to_list()
        right_target_labels = df_right[self.target_column_name].to_list()

        # Compute Gini for each group
        gini_left = compute_gini(left_target_labels)
        gini_right = compute_gini(right_target_labels)

        # Compute counts
        n_left = len(left_target_labels)
        n_right = len(right_target_labels)

        # Compute weighted Gini
        weighted_gini = compute_weighted_gini(gini_left, gini_right, n_left, n_right)

        result = {
            "gini_left": gini_left,
            "gini_right": gini_right,
            "n_left": n_left,
            "n_right": n_right,
            "weighted_gini": weighted_gini,
        }

        return result
