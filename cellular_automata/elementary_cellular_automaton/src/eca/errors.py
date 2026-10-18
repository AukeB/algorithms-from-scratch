"""Module for custom exceptions raised by the project."""


class EvenGridDimensionError(ValueError):
    """Raised when the configured grid dimension is not an odd number."""


class UnsupportedInitializationModeError(ValueError):
    """Raised when the configured initialization mode is not supported."""


class UnsupportedBoundaryModeError(ValueError):
    """Raised when the configured boundary mode is not supported."""
