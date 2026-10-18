"""Tests for the impurity_metrics module."""

import pytest

from dts.metrics.impurity_metrics import compute_gini, compute_weighted_gini


# Testing the "compute_gini" function.


def test_compute_gini_is_zero_for_empty_group() -> None:
    assert compute_gini([]) == 0.0


def test_compute_gini_is_zero_for_pure_group() -> None:
    assert compute_gini(["a", "a", "a"]) == 0.0


def test_compute_gini_is_half_for_even_two_class_group() -> None:
    assert compute_gini(["a", "a", "b", "b"]) == pytest.approx(0.5)


# Testing the "compute_weighted_gini" function.


def test_compute_weighted_gini_weights_children_by_size() -> None:
    weighted_gini = compute_weighted_gini(0.0, 0.5, n_left=1, n_right=3)

    assert weighted_gini == pytest.approx(0.375)


def test_compute_weighted_gini_is_zero_when_no_samples() -> None:
    assert compute_weighted_gini(0.5, 0.5, n_left=0, n_right=0) == 0.0
