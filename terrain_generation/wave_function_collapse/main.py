"""Module for the entry point of the Wave Function Collapse algorithm."""

from src.wave_function_collapse.config_manager import ConfigManager
from src.wave_function_collapse.bitmap import Bitmap
from src.wave_function_collapse.wfc import WaveFunctionCollapse


def main() -> None:
    """
    Orchestrate the WFC algorithm from config loading through a single execution.

    1. Load and validate the configuration from disk.
    2. Load the bitmap from the configured .xlsx file and build the color mapping.
    3. Apply the color mapping to produce a character-mapped bitmap.
    4. Initialise and run the WFC algorithm.
    """
    # Load configuration file.
    config_manager = ConfigManager()
    config = config_manager.read_config()

    # Bitmap
    bitmap_instance = Bitmap(config=config)
    bitmap = bitmap_instance.bitmap

    color_mapping = bitmap_instance.create_color_mapping(bitmap=bitmap)
    bitmap = bitmap_instance.apply_color_mapping(
        bitmap=bitmap, color_mapping=color_mapping
    )

    wfc = WaveFunctionCollapse(
        config=config,
        bitmap=bitmap,
        color_mapping=color_mapping,
    )

    wfc.collapse_grid()


if __name__ == "__main__":
    main()


"""
TODO
- Add contradiction detection — if any cell's options are intersected to an empty set,
  the algorithm should backtrack to the last collapse decision and try a different tile.
- Add a visualize boolean parameter to WaveFunctionCollapse that skips
  compute_superposition_tile during propagation, significantly improving
  performance when visualization is not needed.
- Implement mode_boundary_conditions: currently only wrap_around is supported in practice;
  clamping, mirroring and noise are validated by Pydantic but never acted on.
- Implement mode_model alternatives: currently only overlapping is supported;
  simple_tiled and tiled are validated by Pydantic but never acted on.
"""
