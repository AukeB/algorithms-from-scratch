"""Tests for the knn_classifier module."""

import numpy as np
import pytest

from knn.errors import NotFittedError, UnsupportedDistanceMetricError
from knn.knn_classifier import KNNClassifier


@pytest.fixture
def two_clusters() -> tuple[np.ndarray, np.ndarray]:
    """Provides a small training set with two well-separated clusters.

    Returns:
        training_data (tuple[np.ndarray, np.ndarray]): Features and labels.
    """
    X_train = np.array([[1.0, 1.0], [1.5, 2.0], [5.0, 5.0], [6.0, 5.5]])
    y_train = np.array(["a", "a", "b", "b"])

    training_data = (X_train, y_train)

    return training_data


# Testing the "__init__" method from the "KNNClassifier" class.


def test_init_stores_hyperparameters() -> None:
    classifier = KNNClassifier(k=3, distance_metric="euclidean")

    assert classifier.k == 3
    assert classifier.distance_metric == "euclidean"


def test_init_rejects_k_below_one() -> None:
    with pytest.raises(ValueError, match="k must be at least 1"):
        KNNClassifier(k=0)


def test_init_rejects_unsupported_distance_metric() -> None:
    with pytest.raises(UnsupportedDistanceMetricError):
        KNNClassifier(k=3, distance_metric="manhattan")


# Testing the "_compute_distance" method from the "KNNClassifier" class.


def test_compute_distance_is_euclidean() -> None:
    classifier = KNNClassifier(k=1)

    distance = classifier._compute_distance(np.array([0.0, 0.0]), np.array([3.0, 4.0]))

    assert distance == pytest.approx(5.0)


# Testing the "_get_neighbors" method from the "KNNClassifier" class.


def test_get_neighbors_returns_k_closest_indices_first(
    two_clusters: tuple[np.ndarray, np.ndarray],
) -> None:
    X_train, y_train = two_clusters
    classifier = KNNClassifier(k=2)
    classifier.fit(X=X_train, y=y_train)

    neighbors_idx = classifier._get_neighbors(np.array([1.2, 1.4]), X_train)

    assert list(neighbors_idx) == [0, 1]


# Testing the "fit" method from the "KNNClassifier" class.


def test_fit_stores_training_data(two_clusters: tuple[np.ndarray, np.ndarray]) -> None:
    X_train, y_train = two_clusters
    classifier = KNNClassifier(k=3)

    classifier.fit(X=X_train, y=y_train)

    assert classifier._X_train is X_train
    assert classifier._y_train is y_train


# Testing the "predict" method from the "KNNClassifier" class.


def test_predict_raises_before_fit() -> None:
    classifier = KNNClassifier(k=3)

    with pytest.raises(NotFittedError):
        classifier.predict(X=np.array([[0.0, 0.0]]))


def test_predict_returns_majority_label_of_neighbours(
    two_clusters: tuple[np.ndarray, np.ndarray],
) -> None:
    X_train, y_train = two_clusters
    classifier = KNNClassifier(k=3)
    classifier.fit(X=X_train, y=y_train)

    predictions = classifier.predict(X=np.array([[1.2, 1.4], [5.5, 5.2]]))

    assert list(predictions) == ["a", "b"]
