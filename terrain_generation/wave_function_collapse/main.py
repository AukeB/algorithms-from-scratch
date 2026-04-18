"""Module for the entry point of the Wave Function Collapse algorithm."""

from src.wave_function_collapse.bitmap import BitmapUtils
from src.wave_function_collapse.wfc import WaveFunctionCollapse
from src.wave_function_collapse.config_manager import ConfigManager
from src.wave_function_collapse.constants import Size


def main() -> None:
    """
    Orchestrate the WFC algorithm from config loading through repeated execution.

    1. Load and validate the configuration from disk.
    2. Read the input bitmap from the configured .xlsx file.
    3. Build the color mapping and apply it to the bitmap.
    4. Construct the grid and tile dimensions from config.
    5. Run the WFC algorithm for 10 iterations.
    """
    # Load configuration file.
    config_manager = ConfigManager()
    config = config_manager.read_config()

    # Bitmap
    bitmap_utils = BitmapUtils(config=config, file_name=config.runtime.file_name)
    bitmap = bitmap_utils.read_bitmap_from_excel()
    color_mapping = bitmap_utils.create_color_mapping(bitmap=bitmap)
    bitmap = bitmap_utils.apply_color_mapping(
        bitmap=bitmap, color_mapping=color_mapping
    )

    # Dimensions
    grid_dimensions = Size(config.runtime.grid_dim, config.runtime.grid_dim)
    tile_dimensions = Size(config.runtime.tile_dim, config.runtime.tile_dim)

    # Run
    for _ in range(10):
        wfc = WaveFunctionCollapse(
            config=config,
            bitmap=bitmap,
            grid_dimensions=grid_dimensions,
            tile_dimensions=tile_dimensions,
            color_mapping=color_mapping,
        )

        wfc.collapse_grid()


if __name__ == "__main__":
    main()
