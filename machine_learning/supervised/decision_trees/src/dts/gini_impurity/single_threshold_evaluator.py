"""Module for evaluating Gini impurity of a single threshold split."""

from polars import DataFrame

from src.dts.metrics.impurity_metrics import compute_gini
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
        n_total (int): Total number of samples.

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
        self.n_total = len(df)

    def _compute_weighted_gini(
        self, gini_left: float, gini_right: float, n_left: int, n_right: int
    ) -> float:
        """Compute weighted Gini impurity for the split.

        Args:
            gini_left (float): Gini impurity of left child.
            gini_right (float): Gini impurity of right child.
            n_left (int): Number of samples in left child.
            n_right (int): Number of samples in right child.

        Returns:
            weighted_gini (float): Weighted Gini across both children.
        """
        if self.n_total == 0:
            return 0.0

        weighted_gini = (n_left / self.n_total) * gini_left + (
            n_right / self.n_total
        ) * gini_right

        return weighted_gini

    def evaluate(self) -> dict:
        """Evaluate the Gini impurity split at this threshold.

        Splits data into left and right groups, computes Gini for each, and
        calculates weighted Gini.

        Returns:
            result (dict): Contains gini_left, gini_right, n_left, n_right, and
                weighted_gini for this threshold.
        """
        # Split data
        left_df, right_df = split_data(
            self.df, self.feature_column_name, self.threshold
        )

        # Get target labels for each group
        left_labels = left_df[self.target_column_name].to_list()
        right_labels = right_df[self.target_column_name].to_list()

        # Compute Gini for each group
        gini_left = compute_gini(left_labels)
        gini_right = compute_gini(right_labels)

        # Compute counts
        n_left = len(left_labels)
        n_right = len(right_labels)

        # Compute weighted Gini
        weighted_gini = self._compute_weighted_gini(
            gini_left, gini_right, n_left, n_right
        )

        result = {
            "gini_left": gini_left,
            "gini_right": gini_right,
            "n_left": n_left,
            "n_right": n_right,
            "weighted_gini": weighted_gini,
        }

        return result
