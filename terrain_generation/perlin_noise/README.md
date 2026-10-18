# Perlin Noise

Procedural noise generation algorithm commonly used to create natural-looking textures, terrain, and other continuous patterns.

The project generates 2D Perlin noise on a grid of random unit gradients and shows it in a PyGame window. Toggle buttons show or hide the grid, the gradient arrows and the noise cells.

## Running

```bash
uv sync
uv run python main.py
```

Settings such as the grid size, the random seed, the smoothing curve and the colors live in `src/perlin_noise/configs/config.yaml`.

## Development

```bash
uv run pytest      # tests, with 100% line and branch coverage of src/
uv run ruff check .
```

## Ideas

- Interactive controls in the window, so the grid can be tweaked while it runs.
- Fractal layers (octaves, persistence, fractional Brownian motion).
- Simplex noise.
- Domain warping.
