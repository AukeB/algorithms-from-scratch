# Voronoi Diagram

Project for generating Voronoi diagrams, which partition a plane into regions based on the nearest of a set of seed points.

The grid is coloured so that every cell belongs to the region of its nearest seed point. The seed points are placed at random cell centres, and their colours are spread evenly around the hue wheel.

## Running

```bash
uv sync
uv run python main.py
```

Grid size, the number of seed points, the frame rate and the colours live in `src/voronoi_diagram/configs/config.yaml`.

## Development

```bash
uv run pytest      # tests, with 100% line and branch coverage of src/
uv run ruff check .
```
