"""Tests for the polygons module."""

from pathlib import Path

from water_ripples.polygons import (
    denormalize_points,
    load_polygon,
    normalize_points,
    rasterize_polygon,
    save_polygon,
)


# Testing the "normalize_points" function.


def test_normalize_points_divides_by_reference_size() -> None:
    normalized = normalize_points(
        points=[(200, 125)], reference_width=400, reference_height=250
    )

    assert normalized == [(0.5, 0.5)]


# Testing the "denormalize_points" function.


def test_denormalize_points_scales_to_target_size() -> None:
    pixel_points = denormalize_points(
        normalized_points=[(0.5, 0.5)], width=400, height=250
    )

    assert pixel_points == [(200, 125)]


# Testing the "save_polygon" and "load_polygon" functions.


def test_save_and_load_polygon_round_trip(tmp_path: Path) -> None:
    polygon_path = tmp_path / "polygon.json"
    points = [(40, 25), (200, 50), (100, 200)]

    save_polygon(
        points=points,
        polygon_path=polygon_path,
        reference_width=400,
        reference_height=250,
    )
    loaded = load_polygon(polygon_path=polygon_path, width=400, height=250)

    assert loaded == points


# Testing the "rasterize_polygon" function.


def test_rasterize_polygon_marks_inside_pixels() -> None:
    square = [(10, 10), (30, 10), (30, 30), (10, 30)]

    mask = rasterize_polygon(points=square, width=40, height=40)

    assert mask.shape == (40, 40)
    assert mask[20, 20]
    assert not mask[5, 5]
