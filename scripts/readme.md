# Scripts Folder

The `scripts/` folder contains preprocessing utilities used to generate the datasets powering the game. These scripts are not required to play the game directly, but they are responsible for creating the similarity CSV files used by the gameplay modes.

---

# Shape Similarity Engine

GPU-accelerated geographic shape comparison using rotation-invariant IoU.

This project computes visual similarity between geographic outlines such as:

* Countries
* U.S. states
* Islands
* Arbitrary polygon datasets

The engine converts geographic polygons into rasterized tensors and compares them using rotation-aware Intersection over Union (IoU) scoring.

The final output is a large similarity graph stored as CSV data that can power:

* Geography games
* Shape search engines
* Educational tools
* Geographic clustering
* Visual similarity exploration
* Spatial reasoning systems

---

# Core Idea

Most geographic similarity systems rely on:

* borders
* neighboring countries
* language
* demographics
* geography metadata

This engine instead focuses purely on:

# visual shape similarity

The system asks:

> “What places look alike?”

Examples:

* Italy vs New Zealand
* Chile vs Vietnam
* Cuba vs Croatia
* Madagascar vs Japan

The goal is to compare geographic outlines the same way a human visually perceives them.

---

# Features

## Rotation-Invariant Similarity

Shapes are compared across many possible rotations.

This allows the engine to detect similarity even when shapes are oriented differently.

Example:

* Chile and Vietnam have strong structural similarity when rotated.
* Italy and New Zealand become more comparable after alignment.

---

## GPU Acceleration

The engine uses PyTorch CUDA acceleration when available.

Large batches of geometric comparisons are processed directly on the GPU using:

* tensor operations
* affine transformations
* batched IoU computation
* rotation grids

This dramatically improves performance for large datasets.

---

## Batched Processing

The system supports fully batched comparison pipelines.

Instead of comparing shapes one-by-one, many shape pairs are processed simultaneously.

This enables:

* faster dataset generation
* lower memory overhead
* scalable pairwise comparison generation

---

## Country + State Support

The engine supports:

* Natural Earth country polygons
* U.S. state polygons
* mixed datasets

The generated CSV can therefore compare:

* country ↔ country
* state ↔ state
* country ↔ state

Example:

* Italy compared against U.S. states
* Japan compared against island states

---

# Pipeline Overview

The shape similarity engine follows several stages.

---

# 1. Dataset Loading

Geographic polygons are loaded using GeoPandas.

## Countries

Countries are loaded from Natural Earth:

```python
world = gpd.read_file(
    "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
)
```

## U.S. States

States are loaded from a GeoJSON dataset:

```python
states = gpd.read_file(
    "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
)
```

Both datasets are projected into:

```plaintext
EPSG:6933
```

which preserves area relationships more consistently for geometric comparison.

---

# 2. Geometry Normalization

Raw geographic polygons vary greatly in:

* scale
* orientation
* coordinate position
* complexity

Before comparison, all shapes are normalized.

## Largest Polygon Selection

MultiPolygon geometries are simplified by selecting the largest connected component:

```python
largest_part(geom)
```

This avoids small islands disproportionately affecting similarity.

---

## Translation to Origin

Shapes are centered around the origin.

The engine computes the bounding box center and translates the geometry:

```python
translate(geom, xoff=..., yoff=...)
```

This removes absolute geographic position from the comparison.

---

## Area Normalization

Shapes are scaled so all polygons have comparable area.

```python
scale_factor = np.sqrt(geom.area)
```

This ensures similarity depends on:

* shape
* proportions
* geometry

rather than raw physical size.

---

# 3. Rasterization

Geographic polygons are converted into raster images.

The engine creates a dense coordinate grid:

```python
np.meshgrid(xs, ys)
```

Each pixel is tested for polygon containment:

```python
geom.contains(pts)
```

The result becomes a binary image tensor:

* 1 = inside shape
* 0 = outside shape

This transforms geographic geometry into a GPU-friendly representation.

---

# 4. Tensor Conversion

Rasterized images are converted into PyTorch tensors:

```python
torch.tensor(img)
```

The tensors are moved directly to GPU memory when CUDA is available.

This allows the engine to perform:

* affine transformations
* rotation operations
* IoU calculations

extremely efficiently.

---

# 5. Rotation-Invariant IoU

The core similarity metric is:

# Intersection over Union (IoU)

IoU measures overlap between two binary masks:

```plaintext
intersection / union
```

Higher IoU means stronger shape similarity.

---

## Rotation Search

Instead of comparing only fixed orientations, the engine rotates shapes across many angles.

Example:

```python
angles = torch.linspace(0, np.pi, steps)
```

For every angle:

1. The second shape is rotated
2. Overlap is computed
3. The best IoU is retained

This makes the similarity score rotation invariant.

---

## GPU Rotation

Rotation is implemented using:

```python
F.affine_grid()
F.grid_sample()
```

These PyTorch functions efficiently generate rotated tensors entirely on the GPU.

---

## Chunked Rotation Processing

Large angle sets can consume substantial memory.

The engine therefore processes rotations in chunks:

```python
angle_chunk=16
```

This reduces VRAM usage while maintaining high throughput.

---

# 6. Pairwise Comparison Generation

Every unique pair of shapes is compared using:

```python
combinations(names, 2)
```

If there are N shapes, the engine computes:

```plaintext
N * (N - 1) / 2
```

unique comparisons.

This creates a complete shape similarity graph.

---

# 7. CSV Generation

Results are stored in a CSV file.

Example columns:

| Column | Description                 |
| ------ | --------------------------- |
| shape1 | First place                 |
| type1  | country/state               |
| shape2 | Second place                |
| type2  | country/state               |
| iou    | Best rotation-invariant IoU |
| angle  | Best matching rotation      |

Example:

```plaintext
shape1,shape2,iou,angle
Italy,New Zealand,0.81,1.57
```

---

# Search Utilities

The engine also includes utility search functions.

---

## Similar Shape Search

```python
search(name)
```

Returns the most visually similar places.

Supports:

* all places
* countries only
* states only

---

## Country-to-State Similarity

```python
country_to_states_from_csv(country)
```

Allows country outlines to be compared directly against U.S. states.

Example:

* Which U.S. states look most like Italy?
* Which state resembles Japan?

---

## Top-K Similarity Graphs

```python
top_k_similar_places()
```

Returns the strongest similarity neighbors for every place.

This effectively builds a geographic similarity network.

---

## Shape Centrality Analysis

```python
count_shape2_from_topk()
```

Counts how frequently shapes appear among top similarity matches.

This can identify:

* highly generic shapes
* geographically central forms
* common outline archetypes

---

# Why Rasterization Instead of Raw Polygons?

Rasterization allows:

* GPU acceleration
* fast tensor math
* efficient rotations
* batched overlap computation
* simplified geometric operations

Direct polygon intersection across many rotations would be significantly slower.

---

# Why IoU?

IoU is useful because it:

* is intuitive
* measures direct overlap
* handles arbitrary polygons
* works well for binary masks
* naturally penalizes mismatches

It produces visually meaningful similarity scores.

---

# Performance Notes

The engine is computationally expensive because every shape must be compared against every other shape across many rotations.

Performance optimizations include:

* CUDA acceleration
* batched tensor operations
* chunked rotation processing
* pre-rasterization
* cached CSV outputs

The expensive calculations only happen during preprocessing.

---

# Applications

Potential uses include:

* Geography games
* Educational tools
* Shape recommendation systems
* Geographic clustering
* AI training datasets
* Spatial reasoning research
* Visual similarity exploration

---

# Example Similarities

Interesting examples discovered by the engine:

* Italy ↔ New Zealand
* Chile ↔ Vietnam
* Cuba ↔ Croatia
* Madagascar ↔ Japan
* Florida ↔ Italy

These relationships emerge purely from geometric structure.

---

# Dependencies

Main libraries:

```plaintext
geopandas
numpy
torch
pandas
shapely
```

Optional:

* CUDA GPU for acceleration

---

# Output

The generated CSV becomes the core dataset powering:

* similarity search
* gameplay systems
* ranking modes
* educational exploration
* geography visualization tools

---

# Philosophy

This project explores geography through visual structure rather than political or cultural information.

It treats geographic outlines as abstract geometric objects and asks:

> Which places *look* alike?

The result is a unique combination of:

* geography
* computer vision
* geometry
* GPU computing
* spatial reasoning
* visual exploration
---

# Flag Similarity Engine

The flag similarity engine computes visual similarity scores between every pair of flags in the dataset.

Instead of relying on a single computer vision technique, the engine combines several different image analysis methods to capture multiple aspects of visual similarity.

The final output is a CSV file containing pairwise similarity scores used throughout the game.

---

## Goal

The objective of the engine is to estimate how visually similar two flags appear to a human observer.

This includes:

* Color similarity
* Structural similarity
* Layout similarity
* Symbol placement
* Overall visual appearance

Examples of visually similar flags:

* Romania vs Chad
* Indonesia vs Monaco
* Nordic cross flags
* Pan-Arab color patterns

---

## Pipeline Overview

The script:

1. Loads all flag PNG files
2. Compares every possible pair of flags
3. Extracts multiple visual feature types
4. Computes similarity scores for each method
5. Saves results into a CSV dataset

The generated CSV becomes the core similarity database used by the Streamlit app.

---

## Technologies Used

The engine uses:

* OpenCV
* OpenAI CLIP
* OpenCLIP
* PyTorch
* PIL
* NumPy
* Scikit-learn
* ImageHash

---

## CLIP Embeddings

The engine uses OpenAI's CLIP model through OpenCLIP.

CLIP is a neural network trained to understand images at a high semantic level.

The model is loaded using:

```python
model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="openai"
)
```

Each flag image is:

1. Loaded with PIL
2. Converted to RGB
3. Preprocessed into CLIP format
4. Passed through the neural network
5. Converted into a numerical embedding vector

The embedding vectors are normalized and compared using cosine similarity.

This helps capture:

* Overall layout similarity
* Shared visual structures
* Similar symbolic arrangements
* High-level appearance patterns

---

## Color Histogram Similarity

The engine also compares color distributions directly.

Using OpenCV, each image is converted into HSV color space:

```python
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
```

The script computes normalized color histograms representing:

* Hue distributions
* Saturation patterns
* Dominant colors
* Color proportions

Histograms are compared using correlation scoring.

This is especially useful for flags with similar palettes.

---

## Edge Feature Similarity

To capture structural layout information, the engine extracts edge features.

The process:

1. Converts the image to grayscale
2. Detects edges using the Canny edge detector
3. Resizes the edge map
4. Flattens it into a feature vector
5. Compares vectors using cosine similarity

This captures:

* Stripe boundaries
* Symbol shapes
* Geometric layouts
* Overall composition structure

---

## Perceptual Hashing

The engine also computes perceptual hashes using:

```python
imagehash.phash(img)
```

Perceptual hashing creates compact image fingerprints based on visual appearance.

Unlike cryptographic hashes, visually similar images produce similar perceptual hashes.

The similarity score is computed using hash distance:

```python
hash_score = 1.0 - (hash_diff / 64.0)
```

---

## Pairwise Comparison Generation

The engine compares every unique pair of flags using:

```python
combinations(names, 2)
```

If there are N flags, the script computes:

```plaintext
N * (N - 1) / 2
```

pairwise comparisons.

This creates a complete similarity graph between all flags in the dataset.

---

## CSV Output

The generated CSV stores:

| Column | Description                    |
| ------ | ------------------------------ |
| shape1 | First flag                     |
| shape2 | Second flag                    |
| iou    | Main gameplay similarity score |
| clip   | CLIP embedding similarity      |
| color  | Color histogram similarity     |
| edge   | Edge                           |
| hash   | Hash similarity                |
