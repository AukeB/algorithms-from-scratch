"""Module for the Pydantic configuration models."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

Variant = Literal["baseline", "trapezoid", "image"]


class ConfiguredBaseModel(BaseModel):
    """Config that disallows extra parameters not explicitly defined."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Config that combines all parameters."""

    class Window(ConfiguredBaseModel):
        """Window size. Both None means a windowed size based on the desktop.

        Attributes:
            window_width (int | None): Window width in pixels.
            window_height (int | None): Window height in pixels.
        """

        window_width: int | None
        window_height: int | None

    class Simulation(ConfiguredBaseModel):
        """Parameters shared by every variant.

        Attributes:
            number_of_columns (int): Number of columns in the simulation grid.
            damping (float): Factor between 0 and 1 that reduces wave amplitude.
            wave_brightness (int): Intensity of a splash.
            maximum_brightness (int): Maximum brightness the visualization shows.
            cursor_splash_size (int): Half-width of the disturbed square under the
                cursor.
            framerate (int): Target frames per second.
            background_color (tuple[int, int, int]): Background color of the canvas.
        """

        number_of_columns: int
        damping: float
        wave_brightness: int
        maximum_brightness: int
        cursor_splash_size: int
        framerate: int
        background_color: tuple[int, int, int]

    class Baseline(ConfiguredBaseModel):
        """Options only used by the baseline variant.

        Attributes:
            render_mode (str): "surfarray" blits the whole array at once, "rectangle"
                draws each cell separately.
            rgb_mode (str): How the state becomes RGB: "grayscale", "colormap" or
                "scaled_colormap".
            propagate_mode (str): How the next state is computed: "numba", "numpy" or
                "iterative".
        """

        render_mode: Literal["surfarray", "rectangle"]
        rgb_mode: Literal["grayscale", "colormap", "scaled_colormap"]
        propagate_mode: Literal["numba", "numpy", "iterative"]

    class Trapezoid(ConfiguredBaseModel):
        """Normalized trapezoid (0 is top/left, 1 is bottom/right) and its perspective.

        Used by the trapezoid and image variants.

        Attributes:
            y_top (float): Normalized row where the trapezoid starts.
            y_bottom (float): Normalized row where the trapezoid ends.
            x_top_left (float): Normalized left edge at the top.
            x_top_right (float): Normalized right edge at the top.
            x_bottom_left (float): Normalized left edge at the bottom.
            x_bottom_right (float): Normalized right edge at the bottom.
            perspective_exponent (float): Strength of the perspective. Only used by the
                trapezoid variant.
        """

        y_top: float
        y_bottom: float
        x_top_left: float
        x_top_right: float
        x_bottom_left: float
        x_bottom_right: float
        perspective_exponent: float

    class Image(ConfiguredBaseModel):
        """Files and reference size for the image variant and the mask scripts.

        Attributes:
            image_path (Path): Background photograph.
            mask_path (Path): Boolean lake mask (.npy).
            polygon_path (Path): Normalized polygon the mask is generated from.
            reference_width (int): Width the polygon and mask were drawn at.
            reference_height (int): Height the polygon and mask were drawn at.
            perspective_start (float): Strength of the perspective. Only used by the
                image variant.
        """

        image_path: Path
        mask_path: Path
        polygon_path: Path
        reference_width: int
        reference_height: int
        perspective_start: float

    variant: Variant
    window: Window
    simulation: Simulation
    baseline: Baseline
    trapezoid: Trapezoid
    image: Image
