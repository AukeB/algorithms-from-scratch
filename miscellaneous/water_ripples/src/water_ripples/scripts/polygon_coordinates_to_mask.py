"""Script for generating the lake mask from the saved polygon.

Run it from the project root with:

    uv run python -m water_ripples.scripts.polygon_coordinates_to_mask
"""

import logging

from water_ripples.config_manager import ConfigManager
from water_ripples.masks import save_mask
from water_ripples.polygons import load_polygon, rasterize_polygon

logger = logging.getLogger(__name__)


def main() -> None:
    """Load the configuration, rasterize the saved polygon and save it as the mask."""
    logging.basicConfig(level=logging.INFO)

    config = ConfigManager().load_config_file()
    image_config = config.image

    points = load_polygon(
        polygon_path=image_config.polygon_path,
        width=image_config.reference_width,
        height=image_config.reference_height,
    )
    mask = rasterize_polygon(
        points=points,
        width=image_config.reference_width,
        height=image_config.reference_height,
    )
    save_mask(mask=mask, mask_path=image_config.mask_path)

    logger.info(f"Saved mask of shape {mask.shape} to {image_config.mask_path}")


if __name__ == "__main__":
    main()
