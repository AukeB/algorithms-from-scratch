"""Module for running the k-nearest neighbours classifier on a small example dataset."""

import logging

import numpy as np

from knn.knn_classifier import KNNClassifier

logger = logging.getLogger(__name__)


def main() -> None:
    """Fits a classifier on a small two-cluster dataset and logs its predictions."""
    logging.basicConfig(level=logging.INFO)

    X_train = np.array([[1.0, 1.0], [1.5, 2.0], [5.0, 5.0], [6.0, 5.5]])
    y_train = np.array(["a", "a", "b", "b"])
    X_new = np.array([[1.2, 1.4], [5.5, 5.2]])

    classifier = KNNClassifier(k=3)
    classifier.fit(X=X_train, y=y_train)
    predictions = classifier.predict(X=X_new)

    logger.info("Predictions: %s", predictions)


if __name__ == "__main__":
    main()
