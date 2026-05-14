# Scripts Folder

The `scripts/` folder contains preprocessing utilities used to generate the datasets powering the game. These scripts are not required to play the game directly, but they are responsible for creating the similarity CSV files used by the gameplay modes.

One of the main preprocessing systems is the flag similarity engine.

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
