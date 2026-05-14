from PIL import Image
import imagehash
import cv2
import numpy as np
from itertools import combinations
import pandas as pd
import torch
import open_clip


from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# DEVICE
# =========================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# =========================================================
# LOAD CLIP MODEL
# =========================================================

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="openai"
)

model.eval()
model.to(DEVICE)


# =========================================================
# CLIP EMBEDDING
# =========================================================

def get_clip_embedding(path):

    img = Image.open(path).convert("RGB")

    x = preprocess(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        emb = model.encode_image(x)

    emb = emb.cpu().numpy().flatten()

    emb = emb / np.linalg.norm(emb)

    return emb


# =========================================================
# COLOR HISTOGRAM
# =========================================================

def get_color_histogram(path):

    img = cv2.imread(path)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hist = cv2.calcHist(
        [hsv],
        [0, 1],
        None,
        [32, 32],
        [0, 180, 0, 256]
    )

    hist = cv2.normalize(hist, hist).flatten()

    return hist


# =========================================================
# EDGE FEATURES
# =========================================================

def get_edge_features(path):

    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    edges = cv2.Canny(img, 100, 200)

    edges = cv2.resize(edges, (128, 128))

    edges = edges.flatten().astype(np.float32)

    edges /= 255.0

    return edges


# =========================================================
# PERCEPTUAL HASH
# =========================================================

def get_hash(path):

    img = Image.open(path).convert("RGB")

    return imagehash.phash(img)


# =========================================================
# MAIN COMPARISON
# =========================================================

def compare_images(img1_path, img2_path):

    # ---------- CLIP ----------
    emb1 = get_clip_embedding(img1_path)
    emb2 = get_clip_embedding(img2_path)

    clip_score = cosine_similarity(
        [emb1],
        [emb2]
    )[0][0]

    # ---------- COLOR ----------
    hist1 = get_color_histogram(img1_path)
    hist2 = get_color_histogram(img2_path)

    color_score = cv2.compareHist(
        hist1.astype(np.float32),
        hist2.astype(np.float32),
        cv2.HISTCMP_CORREL
    )

    # ---------- EDGE ----------
    edge1 = get_edge_features(img1_path)
    edge2 = get_edge_features(img2_path)

    edge_score = cosine_similarity(
        [edge1],
        [edge2]
    )[0][0]

    # ---------- HASH ----------
    hash1 = get_hash(img1_path)
    hash2 = get_hash(img2_path)

    hash_diff = hash1 - hash2

    hash_score = 1.0 - (hash_diff / 64.0)

    # ---------- PRINT ----------
    print("\nCOMPARISON RESULTS")
    print("=" * 40)

    print(f"CLIP Similarity : {clip_score:.4f}")
    print(f"Color Similarity: {color_score:.4f}")
    print(f"Edge Similarity : {edge_score:.4f}")
    print(f"Hash Difference : {hash_diff}")
    print(f"Hash Similarity : {hash_score:.4f}")

    print("-" * 40)
    print(f"FINAL SCORE     : {final_score:.4f}")
    return 0
  
def build_similarity_csv(
    folder="png_flags",
    output_csv="flag_similarity.csv"
):

    # get png files
    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".png")
    ]

    # full paths
    paths = {
        os.path.splitext(f)[0]: os.path.join(folder, f)
        for f in files
    }

    names = list(paths.keys())
    results = []

    print(names)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:

        total = len(names) * (len(names) - 1) // 2

        for i, (name1, name2) in enumerate(combinations(names, 2)):
          print(f"[{i+1}/{total}] {name1} vs {name2}")
          img1_path = paths[name1]
          img2_path = paths[name2]

          emb1 = get_clip_embedding(img1_path)
          emb2 = get_clip_embedding(img2_path)

          clip_score = cosine_similarity(
              [emb1],
              [emb2]
          )[0][0]

          # ---------- COLOR ----------
          hist1 = get_color_histogram(img1_path)
          hist2 = get_color_histogram(img2_path)

          color_score = cv2.compareHist(
              hist1.astype(np.float32),
              hist2.astype(np.float32),
              cv2.HISTCMP_CORREL
          )

          # ---------- EDGE ----------
          edge1 = get_edge_features(img1_path)
          edge2 = get_edge_features(img2_path)

          edge_score = cosine_similarity(
              [edge1],
              [edge2]
          )[0][0]

          # ---------- HASH ----------
          hash1 = get_hash(img1_path)
          hash2 = get_hash(img2_path)

          hash_diff = hash1 - hash2

          hash_score = 1.0 - (hash_diff / 64.0)
          iou_score = clip_score

          results.append({
            "shape1": name1,
            "shape2": name2,
            "iou": round(iou_score, 6),
            "clip": round(clip_score, 6),
            "color": round(color_score, 6),
            "edge": round(edge_score, 6),
            "hash": round(hash_score, 6)
        })
          
    df = pd.DataFrame(results)

    df.to_csv(output_csv, index=False)

    print("\nSaved:", output_csv)

svgs_to_pngs()