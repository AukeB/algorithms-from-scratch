"""Tests for the gini_impurity_evaluator module."""

import polars as pl
import pytest

from dts.gini_impurity.gini_impurity_evaluator import GiniImpurityEvaluator


def _make_evaluator(thresholds: list[float]) -> GiniImpurityEvaluator:
    """Create an evaluator on a dataset that separates cleanly at 5.5.

    Args:
        thresholds (list[float]): Candidate thresholds to evaluate.

    Returns:
        evaluator (GiniImpurityEvaluator): Evaluator for the "sepal_length" feature.
    """
    df = pl.DataFrame(
        {"sepal_length": [4.0, 5.0, 6.0, 7.0], "species": ["a", "a", "b", "b"]}
    )

    evaluator = GiniImpurityEvaluator(df, "sepal_length", "species", thresholds)

    return evaluator


# Testing the "__init__" method from the "GiniImpurityEvaluator" class.


def test_init_starts_with_empty_results() -> None:
    evaluator = _make_evaluator([4.5, 5.5])

    assert evaluator.results == {}


# Testing the "evaluate_all_thresholds" method from the "GiniImpurityEvaluator" class.


def test_evaluate_all_thresholds_stores_result_per_threshold() -> None:
    evaluator = _make_evaluator([4.5, 5.5])

    evaluator.evaluate_all_thresholds()

    assert set(evaluator.results) == {4.5, 5.5}
    assert evaluator.results[5.5]["weighted_gini"] == 0.0


# Testing the "get_best_threshold" method from the "GiniImpurityEvaluator" class.


def test_get_best_threshold_returns_lowest_weighted_gini() -> None:
    evaluator = _make_evaluator([4.5, 5.5, 6.5])
    evaluator.evaluate_all_thresholds()

    best_threshold = evaluator.get_best_threshold()

    assert best_threshold == 5.5


def test_get_best_threshold_raises_before_evaluation() -> None:
    evaluator = _make_evaluator([4.5, 5.5])

    with pytest.raises(ValueError, match="Call evaluate_all_thresholds"):
        evaluator.get_best_threshold()
