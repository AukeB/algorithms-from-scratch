# Algorithms from scratch

This repository contains implementations of algorithms without using any ML, AI or other packages that do the job for you.

## Algorithms

```
├── cellular_automata/
│   └── elementary_cellular_automaton/
├── machine_learning/
│   ├── supervised/
│   │   ├── decision_trees/
│   │   └── nearest_neighbours/
│   └── tokenization/
│       └── gpt_tokenizer/
├── miscellaneous/
│   └── water_ripples/
└── terrain_generation/
    ├── perlin_noise/
    ├── voronoi_diagram/
    └── wave_function_collapse/
```

- **Elementary Cellular Automaton**: Python/PyGame implementation of the Elementary Cellular Automaton algorithm, which simulates one-dimensional cellular automata where each cell evolves based on its three-cell neighborhood and an 8-bit rule number.
- **Decision Tree**: Python implementation of a simple decision tree for classification.
- **Nearest Neighbors**: Simple implementation of the K-nearest neighbours algorithm for classifying data based on the classes of nearby points.
- **GPT Tokenizer**: Implementation of a tokenizer similar to the GPT model, which converts text into smaller units for processing by language models.
- **2D Water Ripple Simulation**: This project contains three implementations of a 2D water ripple simulation using PyGame, each building on the previous one. The simulation is based on a discrete wave equation described in [Hugo Elias's classic water ripple tutorial](https://web.archive.org/web/20160418004149/http://freespace.virgin.net/hugo.elias/graphics/x_water.htm).
- **Perlin Noise**: Procedural noise generation algorithm commonly used to create natural-looking textures, terrain, and other continuous patterns.
- **Voronoi Diagram**: Project for generating Voronoi diagrams, which partition a plane into regions based on the nearest of a set of seed points.
- **Wave Function Collapse**: Constraint-based algorithm that generates a 2D grid of tiles locally consistent with a source bitmap, respecting local adjacency rules, often used in procedural content generation.