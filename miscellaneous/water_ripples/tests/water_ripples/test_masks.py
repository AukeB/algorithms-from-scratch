"""Tests for the masks module."""

from pathlib import Path

import numpy as np

from water_ripples.masks import load_mask, resize_bool_mask_nearest, save_mask


# Testing the "resize_bool_mask_nearest" function.


def test_resize_bool_mask_nearest_repeats_each_cell() -> None:
    mask = np.array([[True, False], [False, True]])

    resized = resize_bool_mask_nearest(mask, 4, 4)

    expected = np.array(
        [
            [True, True, False, False],
            [True, True, False, False],
            [False, False, True, True],
            [False, False, True, True],
        ]
    )
    assert resized.shape == (4, 4)
    assert np.array_equal(resized, expected)


# Testing the "load_mask" function.


def test_load_mask_resizes_when_shape_differs(tmp_path: Path) -> None:
    mask_path = tmp_path / "mask.npy"
    save_mask(mask=np.ones((2, 2), dtype=bool), mask_path=mask_path)

    mask = load_mask(mask_path=mask_path, height=4, width=6)

    assert mask.shape == (4, 6)
    assert mask.dtype == bool


def test_load_mask_keeps_matching_shape(tmp_path: Path) -> None:
    mask_path = tmp_path / "mask.npy"
    original = np.array([[True, False], [False, True]])
    save_mask(mask=original, mask_path=mask_path)

    mask = load_mask(mask_path=mask_path, height=2, width=2)

    assert np.array_equal(mask, original)


# Testing the "save_mask" function.


def test_save_mask_writes_npy_file(tmp_path: Path) -> None:
    mask_path = tmp_path / "mask.npy"

    save_mask(mask=np.array([[True]]), mask_path=mask_path)

    assert np.array_equal(np.load(mask_path), np.array([[True]]))
