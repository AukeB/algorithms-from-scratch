"""Module for the k-nearest neighbours classifier."""

from collections import Counter

import numpy as np

from knn.errors import NotFittedError, UnsupportedDistanceMetricError

_SUPPORTED_DISTANCE_METRICS: tuple[str, ...] = ("euclidean",)


class KNNClassifier:
    """Classifies points by a majority vote among their k nearest training
    points.

    Attributes:
        k (int): Number of nearest neighbours that vote on each prediction.
        distance_metric (str): Name of the metric used to measure distance
            between points.
        _X_train (np.ndarray | None): Training features, one row per sample.
        _y_train (np.ndarray | None): Training labels, one entry per sample.

    Example:
        >>> classifier = KNNClassifier(k=3)
        >>> classifier.fit(X=X_train, y=y_train)
        >>> predictions = classifier.predict(X=X_new)
    """

    def __init__(self, k: int, distance_metric: str = "euclidean") -> None:
        """Stores the hyperparameters and prepares an unfitted classifier.

        Args:
            k (int): Number of nearest neighbours that vote on each prediction.
                Must be at least 1.
            distance_metric (str): Name of the distance metric. Defaults to
                "euclidean".

        Raises:
            ValueError: If k is smaller than 1.
            UnsupportedDistanceMetricError: If the distance metric is not
                supported.
        """
        if k < 1:
            raise ValueError(f"k must be at least 1, got {k}.")

        if distance_metric not in _SUPPORTED_DISTANCE_METRICS:
            raise UnsupportedDistanceMetricError(
                f"Unsupported distance metric: {distance_metric!r}."
            )

        self.k = k
        self.distance_metric = distance_metric

        self._X_train: np.ndarray | None = None
        self._y_train: np.ndarray | None = None

    def _compute_distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Computes the distance between two points using the configured metric.

        Args:
            x1 (np.ndarray): First point.
            x2 (np.ndarray): Second point, with the same number of features as
                x1.

        Returns:
            distance (float): Distance between x1 and x2.
        """
        squared_differences = (x1 - x2) ** 2
        sum_of_squares = np.sum(squared_differences)
        distance = np.sqrt(sum_of_squares)

        return distance

    def _get_neighbors(self, x: np.ndarray, X_train: np.ndarray) -> np.ndarray:
        """Finds the indices of the k training points closest to a point.

        Args:
            x (np.ndarray): Point to find the neighbours of.
            X_train (np.ndarray): Training features, one row per sample.

        Returns:
            neighbors_idx (np.ndarray): Indices of the k nearest training
                points, closest first.
        """
        distances = [self._compute_distance(x, x_train) for x_train in X_train]
        sorted_idx = np.argsort(distances)
        neighbors_idx = sorted_idx[: self.k]

        return neighbors_idx

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Stores the training data.

        Args:
            X (np.ndarray): Training features, one row per sample.
            y (np.ndarray): Training labels, one entry per sample.
        """
        self._X_train = X
        self._y_train = y

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicts the label of each point by majority vote of its nearest
        neighbours.

        Args:
            X (np.ndarray): Points to classify, one row per point.

        Returns:
            predictions (np.ndarray): Predicted label for each point in X.

        Raises:
            NotFittedError: If fit has not been called yet.
        """
        if self._X_train is None or self._y_train is None:
            raise NotFittedError("Call fit before predict.")

        X_train = self._X_train
        y_train = self._y_train

        labels = []

        for x in X:
            neighbors_idx = self._get_neighbors(x, X_train)
            neighbor_labels = y_train[neighbors_idx]
            votes = Counter(neighbor_labels)
            most_common = votes.most_common(1)
            label = most_common[0][0]
            labels.append(label)

        predictions = np.array(labels)

        return predictions
