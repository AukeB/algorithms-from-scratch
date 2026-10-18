"""Module for loading, saving and resizing the boolean lake mask."""

from pathlib import Path

import numpy as np


def resize_bool_mask_nearest(mask: np.ndarray, out_h: int, out_w: int) -> np.ndarray:
    """Scale a 2D boolean mask to (out_h, out_w) with nearest-neighbor sampling.

    Args:
        mask (np.ndarray): A 2D boolean array to resize.
        out_h (int): The desired output height in pixels.
        out_w (int): The desired output width in pixels.

    Returns:
        resized_mask (np.ndarray): A 2D boolean array of shape (out_h, out_w).
    """
    in_h, in_w = int(mask.shape[0]), int(mask.shape[1])

    scaled_rows = np.arange(out_h, dtype=np.float64) * in_h / out_h
    floored_rows = np.floor(scaled_rows)
    y_src = np.clip(floored_rows.astype(np.intp), 0, in_h - 1)

    scaled_columns = np.arange(out_w, dtype=np.float64) * in_w / out_w
    floored_columns = np.floor(scaled_columns)
    x_src = np.clip(floored_columns.astype(np.intp), 0, in_w - 1)

    resized_mask = mask[y_src[:, None], x_src[None, :]]

    return resized_mask


def load_mask(mask_path: Path, height: int, width: int) -> np.ndarray:
    """Load the lake mask and resize it to the window if its shape differs.

    Args:
        mask_path (Path): Path to the .npy file with the mask.
        height (int): Height of the window in pixels.
        width (int): Width of the window in pixels.

    Returns:
        mask (np.ndarray): A boolean array of shape (height, width).
    """
    raw_mask = np.load(mask_path)
    mask = np.asarray(raw_mask)

    if mask.shape[0] != height or mask.shape[1] != width:
        mask = resize_bool_mask_nearest(mask, height, width)

    bool_mask = mask.astype(bool)

    return bool_mask


def save_mask(mask: np.ndarray, mask_path: Path) -> None:
    """Save a boolean mask as a .npy file.

    Args:
        mask (np.ndarray): The boolean mask to save.
        mask_path (Path): Destination .npy file.
    """
    np.save(mask_path, mask)
