"""Shared default parameters for water ripple demo modules."""

from pathlib import Path

# Size and dimension related parameters (all three: water_ripples.py,
# water_ripples_in_image.py, water_ripples_trapezoid.py).
# Window width/height default to a fraction of the desktop (see utils_screen);
# row count follows aspect ratio unless overridden in WaterRipples.__init__.
NUMBER_OF_COLUMNS = 200
WINDOW_SIZE_SCREEN_FRACTION = 0.90

# Algorithm related parameters (all three)
DAMPING = 0.99
WAVE_BRIGHTNESS = 255
MAXIMUM_BRIGHTNESS = 255
CURSOR_SPLASH_SIZE = 1
FRAMERATE = 60
BACKGROUND_COLOR = (0, 0, 0)

# Modes — only used in water_ripples.py
RENDER_MODE = "surfarray"  # Options are ["surfarray", "rectangle"]
RGB_MODE = "scaled_colormap"  # Options are ["grayscale", "colormap", "scaled_colormap"]
PROPAGATE_MODE = "numba"  # Options are ["numba", "numpy", "iterative"]

# Image paths — only used in water_ripples_in_image.py
_LAKE_DATA_DIR = Path("data/lake_1")
IMAGE_PATH = _LAKE_DATA_DIR / "image.jpg"
MASK_PATH = _LAKE_DATA_DIR / "mask.npy"

# Trapezoid related parameters — used in water_ripples_in_image.py and
# water_ripples_trapezoid.py (not water_ripples.py).
"""
This variable defines the normalized coordinates of a trapezoid.
A trapezoid is a four-side polygon with at least one pair of parallel sides, known as the bases. In
our case the parallel sides are the two horizontal lines.

- For 'y', 0 corresponds with top of the window, 1 would be the bottom of the window.
- For 'x', 0 corresponds with the left side of the window, 1 would be the right side.
"""
NORMALIZED_TRAPEZOID: dict = {
    "y_top": 0.4,
    "y_bottom": 1,
    "x_top_left": 0.0,
    "x_top_right": 1.0,
    "x_bottom_left": 0.2,
    "x_bottom_right": 1,
}

# Only used in water_ripples_trapezoid.py
"""
This variable determines the 'amount' of persective you see in the trapezoid window

Exponent = 0: Completely flat, no perspective at all.
Exponent = 1 (linear): Equal distribution — every row gets progressively a little taller than the
    previous, but the difference between rows is constant. Not much perspective feel.
Exponent = 2 (quadratic): Moderate perspective — rows grow noticeably faster toward the bottom.
Exponent = 3 (cubic): Strong perspective — rows at the bottom are much taller than rows at the top.
Exponent > 3: Very heavy perspective — the top rows become extremely compressed, almost invisible,
    and the bottom rows dominate. Can look unrealistic.
"""
PERSPECTIVE_EXPONENT = 1
