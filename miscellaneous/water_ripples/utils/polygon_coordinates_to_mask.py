"""
One-off tool for generating a boolean mask from a polygon defined in a JSON file.
Because it is a one-off tool this has been entirely generated with an LLM.
"""

import json
import numpy as np
import pygame as pg

from pathlib import Path

# Config
WINDOW_WIDTH = 4000
WINDOW_HEIGHT = 2500
DIR_PATH = Path("data/lake_1")
IMAGE_PATH = DIR_PATH / "image.jpg"
MASK_PATH = DIR_PATH / "mask.npy"
POLYGON_PATH = DIR_PATH / "polygon_coordinates_test.json"


def main() -> None:
    # Load normalized points and denormalize to pixel coordinates
    with open(str(POLYGON_PATH), "r") as f:
        normalized_points = json.load(f)

    pixel_points = [
        (int(x * WINDOW_WIDTH), int(y * WINDOW_HEIGHT)) for x, y in normalized_points
    ]

    # Use pygame to rasterize the polygon onto a surface
    pg.init()
    surface = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    surface.fill((0, 0, 0))
    pg.draw.polygon(surface, (255, 255, 255), pixel_points)

    # Convert surface to numpy array and threshold to boolean mask
    rgb_array = pg.surfarray.array3d(surface)  # shape: (width, height, 3)
    mask = rgb_array[:, :, 0] > 128  # shape: (width, height), True inside polygon
    mask = mask.T  # Transpose to (height, width) to match numpy convention

    np.save(MASK_PATH, mask)
    print(f"Saved mask of shape {mask.shape} to {MASK_PATH}")

    pg.quit()


main()
