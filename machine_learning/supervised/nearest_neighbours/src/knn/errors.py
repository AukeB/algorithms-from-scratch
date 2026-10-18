"""Module for custom exceptions raised by the k-nearest neighbours package."""


class UnsupportedDistanceMetricError(ValueError):
    """Raised when the requested distance metric is not supported."""


class NotFittedError(RuntimeError):
    """Raised when predictions are requested before the classifier has been fitted."""
