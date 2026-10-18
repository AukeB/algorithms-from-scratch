# Water ripples simulation

A 2D water ripple simulation using PyGame. It is based on a discrete wave equation described in [Hugo Elias's classic water ripple tutorial](https://web.archive.org/web/20160418004149/http://freespace.virgin.net/hugo.elias/graphics/x_water.htm).

Three variants share one core, and the configuration file picks which one runs:

- **`baseline`**: a flat grid that fills the window. Render, colour and propagation modes can be switched in the config.
- **`trapezoid`**: the grid is projected onto a trapezoid, so rows narrow toward the top for a sense of depth.
- **`image`**: the trapezoid effect drawn over a photograph of a lake. The wave overlay is only drawn where a precomputed lake mask is set, and its transparency follows the wave amplitude.

---

## Running

Run from the project root, since the paths in the config are relative to it:

```bash
uv sync
uv run python main.py
```

Which variant runs is set by `variant` in `src/water_ripples/configs/config.yaml`:

```yaml
variant: image # "baseline", "trapezoid" or "image"
```

Each variant's options live in its own section of the same file. The `image` section also holds the file paths and the reference size that the scripts below use.

---

## Creating a lake mask from a new image

The `image` variant needs a mask of the water. Two scripts make it from a polygon that is clicked on the image:

1. Draw the polygon on the reference image. Left click adds a point, Z undoes it, Enter saves (at least three points), and ESC quits:

   ```bash
   uv run python -m water_ripples.scripts.get_polygon_coordinates
   ```

2. Rasterize the saved polygon into the mask:

   ```bash
   uv run python -m water_ripples.scripts.polygon_coordinates_to_mask
   ```

The polygon is stored with normalized coordinates, so it works at any resolution. The mask is saved at the reference size in the config.

---

## Development

```bash
uv run pytest      # tests, with 100% line and branch coverage of src/
uv run ruff check .
```

Tests run PyGame headless with the SDL dummy drivers, and numba-compiled kernels run as plain Python so coverage can trace them.
