"""Entry point for the Wave Function Collapse algorithm."""

import logging
import time

from wave_function_collapse.bitmap import Bitmap
from wave_function_collapse.config_manager import ConfigManager
from wave_function_collapse.errors import ContradictionError
from wave_function_collapse.wfc import WaveFunctionCollapse
from wave_function_collapse.wfc_visualizer import WFCVisualizer

logger = logging.getLogger(__name__)

_FINAL_FRAME_HOLD_SECONDS = 3


def main() -> None:
    """Load the bitmap, run the algorithm, and show the result for a few seconds."""
    logging.basicConfig(level=logging.INFO)

    config = ConfigManager().read_config()

    bitmap_instance = Bitmap(config=config)
    color_mapping = bitmap_instance.create_color_mapping(bitmap=bitmap_instance.bitmap)
    mapped_bitmap = bitmap_instance.apply_color_mapping(
        bitmap=bitmap_instance.bitmap,
        color_mapping=color_mapping,
    )

    visualizer = WFCVisualizer(config=config, color_mapping=color_mapping)
    wfc = WaveFunctionCollapse(
        config=config,
        bitmap=mapped_bitmap,
        color_mapping=color_mapping,
        visualizer=visualizer,
    )

    try:
        wfc.collapse_grid()
    except ContradictionError as error:
        logger.error(f"{error} Restart the run to try again.")

    time.sleep(_FINAL_FRAME_HOLD_SECONDS)
    visualizer.quit()


if __name__ == "__main__":
    main()
