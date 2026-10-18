"""Tests for the single_threshold_evaluator module."""

import polars as pl

from dts.gini_impurity.single_threshold_evaluator import SingleThresholdGiniEvaluator


# Testing the "evaluate" method from the "SingleThresholdGiniEvaluator" class.


def test_evaluate_returns_gini_metrics_for_split() -> None:
    df = pl.DataFrame(
        {"sepal_length": [4.0, 5.0, 6.0, 7.0], "species": ["a", "a", "b", "b"]}
    )
    evaluator = SingleThresholdGiniEvaluator(df, "sepal_length", "species", 5.5)

    result = evaluator.evaluate()

    assert result == {
        "gini_left": 0.0,
        "gini_right": 0.0,
        "n_left": 2,
        "n_right": 2,
        "weighted_gini": 0.0,
    }


def test_evaluate_reports_impure_split() -> None:
    df = pl.DataFrame(
        {"sepal_length": [4.0, 5.0, 6.0, 7.0], "species": ["a", "b", "a", "b"]}
    )
    evaluator = SingleThresholdGiniEvaluator(df, "sepal_length", "species", 5.5)

    result = evaluator.evaluate()

    assert result["gini_left"] == 0.5
    assert result["gini_right"] == 0.5
    assert result["weighted_gini"] == 0.5
