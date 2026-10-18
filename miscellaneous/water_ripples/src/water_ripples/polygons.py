"""Module for saving, loading and rasterizing polygons drawn on the reference image.

Polygons are stored as JSON with normalized [0, 1] coordinates, so they do not depend on the
resolution they were drawn at.
"""

import json
from pathlib import Path

import numpy as np
import pygame as pg


def normalize_points(
    points: list[tuple[int, int]],
    reference_width: int,
    reference_height: int,
) -> list[tuple[float, float]]:
    """Convert pixel points to normalized [0, 1] coordinates.

    Args:
        points (list[tuple[int, int]]): Points in pixel coordinates.
        reference_width (int): Width the points were drawn at.
        reference_height (int): Height the points were drawn at.

    Returns:
        normalized_points (list[tuple[float, float]]): The normalized points.
    """
    normalized_points = [(x / reference_width, y / reference_height) for x, y in points]

    return normalized_points


def denormalize_points(
    normalized_points: list[tuple[float, float]],
    width: int,
    height: int,
) -> list[tuple[int, int]]:
    """Convert normalized [0, 1] coordinates to pixel coordinates.

    Args:
        normalized_points (list[tuple[float, float]]): Points in normalized coordinates.
        width (int): Target width in pixels.
        height (int): Target height in pixels.

    Returns:
        pixel_points (list[tuple[int, int]]): The points in pixel coordinates.
    """
    pixel_points: list[tuple[int, int]] = []

    for x, y in normalized_points:
        pixel_x = int(x * width)
        pixel_y = int(y * height)
        pixel_points.append((pixel_x, pixel_y))

    return pixel_points


def save_polygon(
    points: list[tuple[int, int]],
    polygon_path: Path,
    reference_width: int,
    reference_height: int,
) -> None:
    """Save pixel points as a normalized polygon JSON file.

    Args:
        points (list[tuple[int, int]]): Points in pixel coordinates.
        polygon_path (Path): Destination JSON file.
        reference_width (int): Width the points were drawn at.
        reference_height (int): Height the points were drawn at.
    """
    normalized_points = normalize_points(
        points=points,
        reference_width=reference_width,
        reference_height=reference_height,
    )

    with open(polygon_path, "w") as file:
        json.dump(normalized_points, file, indent=2)


def load_polygon(polygon_path: Path, width: int, height: int) -> list[tuple[int, int]]:
    """Load a normalized polygon JSON file and convert it to pixel coordinates.

    Args:
        polygon_path (Path): The JSON file to read.
        width (int): Target width in pixels.
        height (int): Target height in pixels.

    Returns:
        pixel_points (list[tuple[int, int]]): The polygon in pixel coordinates.
    """
    with open(polygon_path) as file:
        normalized_points: list[tuple[float, float]] = json.load(file)

    pixel_points = denormalize_points(
        normalized_points=normalized_points,
        width=width,
        height=height,
    )

    return pixel_points


def rasterize_polygon(
    points: list[tuple[int, int]],
    width: int,
    height: int,
) -> np.ndarray:
    """Rasterize a polygon into a boolean mask.

    Args:
        points (list[tuple[int, int]]): Polygon corners in pixel coordinates.
        width (int): Width of the mask in pixels.
        height (int): Height of the mask in pixels.

    Returns:
        mask (np.ndarray): A boolean array of shape (height, width), True inside the polygon.
    """
    surface = pg.Surface((width, height))
    surface.fill((0, 0, 0))
    pg.draw.polygon(surface, (255, 255, 255), points)

    rgb_array = pg.surfarray.array3d(surface)
    red_channel = rgb_array[:, :, 0]
    inside = red_channel > 128
    mask = inside.T

    return mask
