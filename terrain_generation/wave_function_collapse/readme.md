# Wave Function Collapse

## Algorithm

The Wave Function Collapse algorithm generates a 2D grid of tiles that is locally consistent with a source bitmap. Every region of the output resembles a region of the input. The algorithm works in three phases: **extraction**, **initialisation**, and **collapse**.

### Phase 1 — Extraction

Before the algorithm can generate anything, it needs to learn what patterns exist in the input bitmap and how they relate to each other.

**1. Read the bitmap**
The input bitmap is provided as an `.xlsx` file where each cell's background color represents a pixel. The bitmap boundary is detected automatically by scanning for an outer border drawn around the bitmap in Excel. Each cell's fill color is read and converted from hex to an RGB tuple.

**2. Build the color mapping**
Each unique RGB color in the bitmap is assigned a unique str identifier starting from A. The bitmap is then converted from a 2D grid of RGB tuples to a 2D grid of string values. This makes subsequent comparisons and hashing significantly faster.

**3. Extract tiles**
Every possible $NxN$ subgrid is extracted from the str-mapped bitmap, where $N$ is the configured tile dimension. Extraction wraps around the edges of the bitmap, treating it as a torus, so tiles are also extracted across the bitmap boundary. This ensures that patterns near the edges are represented equally.

**4. Compute tile weights**
The frequency of each unique tile is counted across all extracted tiles. Each tile's weight is its count divided by the total number of extracted tiles, producing a normalized frequency distribution that sums to 1. These weights are later used to bias the collapse step towards tiles that appear more often in the input.

**5. Compute neighbor compatibility**
For every pair of unique tiles, the algorithm checks compatibility in all four directions. Two tiles are compatible in a given direction if their overlapping slices match. For example, tile A is a valid upward neighbor of tile B if the top $N-1$ rows of tile B are identical to the bottom $N-1$ rows of tile A. All valid neighbor relationships are precomputed and stored in a nested dict for fast lookup during propagation.

---

### Phase 2 — Initialisation

**6. Initialise the grid**
A 2D grid of `GridCell` objects is created with the configured output dimensions. Every cell starts in a superposition of all possible tiles — meaning every unique tile extracted from the bitmap is a valid candidate for every cell. Each cell also maintains a superposition tile: a weighted average of all its current candidate tiles rendered as an RGB image, used for visualisation before the cell collapses.

---

### Phase 3 — Collapse

The collapse phase runs iteratively until every cell in the grid has been assigned exactly one tile.

**7. Find the minimum entropy cell**
On each iteration, the algorithm scans all uncollapsed cells and finds those with the fewest remaining tile options. This is the minimum entropy heuristic — cells with fewer options are more constrained and should be resolved first to minimise the risk of contradictions later. If multiple cells are tied, one is chosen at random.

**8. Collapse the cell**
The chosen cell is collapsed to a single tile, selected at random weighted by the tile frequency distribution. Tiles that appear more often in the input bitmap are more likely to be chosen.

**9. Propagate constraints**
After collapsing a cell, the algorithm recursively propagates the consequences outward to neighboring cells. For each neighboring cell in each direction, the set of still-valid tiles is intersected with the set of tiles that are compatible with the collapsed cell in that direction. Any tiles that are no longer compatible are eliminated from the neighbor's options. This process recurses outward up to a configured `recursion_depth`. Deeper propagation catches more inconsistencies earlier but is more computationally expensive.

**10. Repeat or terminate**
Steps 7–9 repeat until all cells are collapsed. If a cell's options are ever reduced to an empty set, the algorithm has reached a contradiction — no valid tile exists for that cell given the surrounding constraints. The current implementation does not handle contradictions with backtracking; restarting the algorithm is the simplest recovery strategy.

## Definitions

- **Bitmap**: Your input image, that serves as the source image from which $NxN$ patterns are extracted. A bitmap is a type of memory organization or image file format used to store digital images. It consists of a rectangular grid of pixels, where each pixel represents a color or shade. This description sounds similar to a 'normal' image. However, originally a bitmap referred to a binary image, where each pixel was either black or white (1-bit per pixel), in that sense it really is a map of bits. It is often used referring to uncompressed, or minimally processed data. In practice, bitmap often refers to any raster image, meaning an image made of pixels rather than vectors. It can also store multiple bits per pixel (8-bit grayscale, 24-bit color or 32-bit with alpha layer).

- **Pattern/tile**: A square subgrid of $NxN$ cells extracted from the bitmap. Every possible $NxN$ subgrid is extracted from the bitmap, including overlapping ones, with wrapping at the edges so that tiles can also be extracted across the bitmap boundary. A tile is represented in code as a 2D-tuple of string color identifiers. Duplicate tiles are counted to determine frequency weights, which are used during the weighted random collapse step.

- **Grid**: The 2D array of `GridCell` objects that the algorithm fills in during the collapse phase. It has configurable dimensions and starts with every cell in superposition. After the algorithm completes, every cell has been collapsed to a single tile, and the grid represents the generated output.

- **GridCell**: A single element of the grid. Each cell starts in a superposition of all possible tiles and progressively collapses to a single tile as the algorithm propagates constraints from neighboring cells. Before collapsing, the cell maintains a superposition tile for visualization purposes.

- **Superposition**: The state of a grid cell that has not yet been collapsed. A cell in superposition holds a set of tiles that are all still valid candidates given the current constraints from its neighbors. A cell exits superposition when it is collapsed to a single tile.

- **Collapse**: The act of reducing a grid cell from superposition to a single definite tile, chosen at random weighted by tile frequency. Once collapsed, a cell's tile is fixed and its options set is emptied.

- **Entropy**: In the context of this algorithm, entropy is simply the number of remaining valid tile options for a grid cell. A cell with many options has high entropy — it is uncertain. A cell with few options has low entropy — it is constrained. The algorithm always collapses the cell with the lowest entropy first, which is called the minimum entropy heuristic. This reduces the risk of contradictions compared to collapsing cells randomly.

- **Contradiction**: A failure state that occurs when a grid cell's options are reduced to an empty set — no valid tile exists for that cell given the surrounding constraints. The current implementation does not recover from contradictions; the algorithm must be restarted.

- **Neighbors**: Two tiles are considered valid neighbors in a given direction if their overlapping slices match. For example, tile A is a valid upward neighbor of tile B if the top $N−1$ rows of tile B match the bottom $N−1$ rows of tile A. This compatibility check is precomputed for all tile pairs in all four directions before the algorithm starts, and stored in the neighbors dict. During propagation, this dict is used to eliminate tiles from a cell's options that are incompatible with its already-collapsed or constrained neighbors.

## Code variable descriptions

- I have created two `namedtuple` objects in `constants.py`:
    1. `Size` — used for variables that specify pixel dimensions. Variables of this type contain the word `size` in them, for example `tile_size`.
    2. `Dimensions` — used for variables that specify a count of elements in rows and columns. Variables of this type contain the word `dimensions` in them, for example `grid_dimensions`.
- The cells of which the grid consists are referred to as `grid_cell`, and the cells of which a tile consists are called `tile_cell`. A cell of a grid can be filled with a tile, so a grid cell can consist of several tile cells.
- Bitmaps are provided as `.xlsx` files where each cell's background color represents a pixel. The bitmap boundary is detected automatically by scanning for an outer border drawn around the bitmap in Excel.
- Colors are represented internally as `RGBColor` tuples `(r, g, b)` when reading the bitmap, and then mapped to str identifiers `A, B, C, ...` for comparison and hashing during the algorithm.

| Variable name | Type | Type more elaborate | Dimensions | Description |
|---|---|---|---|---|
| `bitmap` | `list` | `list[list[RGBColor]]` | $MxN$ | The raw bitmap read from the Excel file as a 2D list of RGB tuples, before color mapping is applied. |
| `bitmap_dimensions` | `Dimensions` | `Dimensions[int, int]` | $MxN$ | The number of rows and columns your bitmap consists of, auto-detected from the Excel file border. |
| `grid_dimensions` | `Dimensions` | `Dimensions[int, int]` | $MxN$ | The number of grid elements/cells that the grid consists of. In the code this is referred to as `grid_cell`. |
| `grid` | `list` | `list[list[GridCell]]` | $MxN$ | The grid. After the algorithm has completed, this will contain the collapsed cells and the generated pattern based on the bitmap input image. It is a 2D-list of objects of the `GridCell` class. |
| `tile_dimensions` | `Dimensions` | `Dimensions[int, int]` | $NxN$ | The number of elements/cells that a tile consists of. In the code this is referred to as `tile_cell`. |
| `all_tiles` | `list` | `list[Tile]` | - | A list of all the tiles extracted from the bitmap, including duplicates. Used intermediately to compute `tile_weights`, but not used directly by the algorithm after that. |
| `tile_weights` | `dict` | `dict[Tile, float]` | - | A dictionary where for each unique tile the weight is represented as a float value. All weights sum up to 1. |
| `tile_set` | `set` | `set[Tile]` | - | The set of all unique tiles that were extracted from the bitmap. |
| `tile` | `Tile \| None` | `Tile \| None` | $NxN$ | The single tile a `GridCell` has collapsed to. `None` until the cell is collapsed. |
| `superposition_tile` | `list \| None` | `list[list[RGBColor]] \| None` | $NxN$ | A weighted average of all remaining tile options for a cell, rendered as an RGB image. Used for visualization before the cell collapses. Set to `None` once the cell is collapsed. |
| `neighbors` | `dict` | `defaultdict[Tile, defaultdict[str, set[Tile]]]` | - | This variable contains all the information about which tiles are allowed to go next to which tiles. It is a nested defaultdict. The keys in the first dict are all the unique `Tile` instances. Then, for each tile, there are 4 directions: `up`, `down`, `left` and `right`. For each of these 4 directions, the set of valid neighboring tiles is stored as the value. |
| `recursion_depth` | `int` | `int` | - | The maximum number of cells outward that constraints propagate after each collapse step. Configured in `config.yaml` under `general.recursion_depth`. |
| `color_mapping` | `dict` | `dict[RGBColor, str]` | - | A dict mapping each unique RGB tuple extracted from the bitmap to a unique string identifier starting from 'A'. |
| `inverted_color_mapping` | `dict` | `dict[str, RGBColor]` | - | The inverse of `color_mapping` — maps string identifiers back to RGB tuples, used when resolving colors for visualization. |


## Model versions

- The '**Even Simpler Tiled Model**': The simplest version of the algorithm, introduced by Robert Heaton as a stepping stone to understanding the more advanced models. Each tile is a single pixel of a single color, so there are no edge-matching or symmetry concerns. Adjacency rules are defined as 3-tuples of two tiles and a direction — for example `(SEA, COAST, LEFT)` means a sea tile can be placed to the left of a coast tile. These rules can either be written manually or derived automatically by parsing an example input image. Tile frequencies are recorded from the input and used as weights during the collapse step.

- The '**Simple Tiled Model**': An extension of the Even Simpler Tiled Model where tiles are predefined $NxN$ patterns rather than single pixels, and adjacency rules are provided explicitly rather than extracted from a bitmap. This model also accounts for tile symmetry and rotation, meaning a tile and its rotated or mirrored variants are treated as compatible where their edges match. This makes for better output but more complex setup.

- The '**Overlapping Model**': The most advanced model and the one implemented in this codebase. There are no predefined tiles or adjacency rules — both are extracted automatically from the source input bitmap. Every possible $NxN$ subgrid is extracted as a tile, compatibility rules are derived from overlapping slices, and tile weights are computed from observed frequencies. To make this model even more powerful, you can mirror and rotate extracted tiles to expand the tileset and improve output variety. Symmetry properties of the tileset can also be exploited to make the neighbor computation more efficient. These are considered future extensions rather than part of the current implementation.

## Resources

- The [original repository](https://github.com/mxgmn/WaveFunctionCollapse/tree/master) by [mxgmn](https://github.com/mxgmn). However, I don't think the algorithm description is formulated properly. I spent a lot of time trying to figure out what the adjacency rules precisely are for the constraint propagation, also for different versions of the algorithm. I think it could have been written more clearly. I also don't see the point of the quantum mechanics analogy. Introducing this makes it unnecessarily complex; for example, entropy is just a fancy word for the 'number of options' or 'number of possibilities' in the context of the wave function collapse algorithm. You can probably have a good discussion whether it is correct to use quantum mechanical terms in this context, but I think that's besides the point and also wrong. It is wrong because entropy in quantum mechanics or thermodynamics describes a different type of system; it is based on the physical arrangements of molecules on a microscopic level while still appearing the same on the macro level, while in the context of WFC it's just the number of options for an element in your variable that represents the grid. It is besides the point because code should be simple and easy to understand, and trying to explain the concepts related to your procedural generation algorithm in terms of quantum mechanical concepts, doesn't help with this. It does sound fancy though, and it grabs your attention, so I guess it's just good marketing.
- A [blog post](https://www.gridbugs.org/wave-function-collapse/). Haven't read it yet.
- This [blog post](https://robertheaton.com/2018/12/17/wavefunction-collapse-algorithm/) by Robert Heaton is a good one to start with. It explains the algorithm from a basic level and also introduces an even simpler version of the algorithm which makes it easier to understand the more advanced versions.
- [Model synthesis](https://paulmerrell.org/model-synthesis/) by Paul Merrell. A 3-dimensional application of the WFC algorithm.