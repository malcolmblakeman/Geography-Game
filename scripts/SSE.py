"""
Shape Similarity Engine (IoU + Rotation, GPU-Accelerated)

Supports:
- Countries
- US States
- State-only search
"""

import geopandas as gpd
import numpy as np
import torch
import torch.nn.functional as F
import pandas as pd
from shapely.affinity import scale, translate
from shapely import points
from itertools import combinations

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ========================
# GEOMETRY
# ========================

def largest_part(geom):
    if geom.geom_type == "MultiPolygon":
        return max(geom.geoms, key=lambda g: g.area)
    return geom


def normalize(geom):
    geom = geom.buffer(0)

    minx, miny, maxx, maxy = geom.bounds
    geom = translate(geom, xoff=-(minx + maxx)/2, yoff=-(miny + maxy)/2)

    scale_factor = np.sqrt(geom.area)
    geom = scale(geom, xfact=1/scale_factor, yfact=1/scale_factor, origin=(0, 0))

    return geom


# ========================
# RASTERIZE
# ========================

def rasterize(geom, size=192):
    minx, miny, maxx, maxy = geom.bounds

    xs = np.linspace(minx, maxx, size)
    ys = np.linspace(miny, maxy, size)

    xv, yv = np.meshgrid(xs, ys)
    pts = points(xv.ravel(), yv.ravel())

    mask = geom.contains(pts)
    return mask.reshape((size, size)).astype(np.float32)


# ========================
# GPU IOU
# ========================

def compute_iou_rotation_invariant(t1, t2, angles, angle_chunk=16):
    B = t1.shape[0]
    best_vals = torch.zeros(B, device=device)
    best_idx = torch.zeros(B, dtype=torch.long, device=device)

    with torch.no_grad():
        for start in range(0, len(angles), angle_chunk):
            ang_chunk = angles[start:start + angle_chunk]
            chunk_size = len(ang_chunk)

            t2_exp = t2.repeat_interleave(chunk_size, dim=0)

            theta = torch.zeros((B * chunk_size, 2, 3), device=device)
            cos = torch.cos(ang_chunk).repeat(B)
            sin = torch.sin(ang_chunk).repeat(B)

            theta[:, 0, 0] = cos
            theta[:, 0, 1] = -sin
            theta[:, 1, 0] = sin
            theta[:, 1, 1] = cos

            grid = F.affine_grid(theta, (B * chunk_size, 1, t2.shape[2], t2.shape[3]), align_corners=False)
            rotated = F.grid_sample(t2_exp, grid, align_corners=False)

            t1_exp = t1.repeat_interleave(chunk_size, dim=0)

            inter = ((rotated > 0.5) & (t1_exp > 0.5)).sum(dim=(1, 2, 3)).float()
            union = ((rotated > 0.5) | (t1_exp > 0.5)).sum(dim=(1, 2, 3)).float()

            ious = (inter / (union + 1e-6)).view(B, chunk_size)

            vals, idx = torch.max(ious, dim=1)

            better = vals > best_vals
            best_vals[better] = vals[better]
            best_idx[better] = idx[better] + start

            del rotated, grid, theta, t2_exp, t1_exp
            torch.cuda.empty_cache()

    return best_vals, best_idx


# ========================
# DATA LOADING
# ========================

def load_datasets():
    world = gpd.read_file(
        "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    ).to_crs("EPSG:6933")

    states = gpd.read_file(
        "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
    ).to_crs("EPSG:6933")

    return world, states


# ========================
# BUILD CSV
# ========================

def build_similarity_csv(output_csv="shape_similarity.csv", size=256, steps=180):
    world, states = load_datasets()
    tensors = {}
    types = {}

    # Countries
    for name in world["ADMIN"]:
        geom = normalize(largest_part(world[world["ADMIN"] == name].geometry.values[0]))
        img = rasterize(geom, size)

        tensors[name] = torch.tensor(img).unsqueeze(0).unsqueeze(0).to(device)
        types[name] = "country"

    # States
    for name in states["name"]:
        geom = normalize(largest_part(states[states["name"] == name].geometry.values[0]))
        img = rasterize(geom, size)

        key = "Georgia (state)" if name == "Georgia" else name

        tensors[key] = torch.tensor(img).unsqueeze(0).unsqueeze(0).to(device)
        types[key] = "state"

    names = list(tensors.keys())

    angles = torch.linspace(0, np.pi, steps, device=device)

    results = []

    total = len(names) * (len(names) - 1) // 2
    print("Total comparisons:", total)

    for i, (n1, n2) in enumerate(combinations(names, 2)):
        t1 = tensors[n1]["tensor"]
        t2 = tensors[n2]["tensor"]

        rotated = rotate_batch(t2, angles)
        ious = batch_iou(t1, rotated)

        best_idx = torch.argmax(ious).item()
        best_iou = ious[best_idx].item()
        best_angle = angles[best_idx].item() * 180 / np.pi

        results.append({
            "shape1": n1,
            "type1": tensors[n1]["type"],
            "shape2": n2,
            "type2": tensors[n2]["type"],
            "iou": best_iou,
            "angle_deg": best_angle
        })

        if (i + 1) % 229 == 0:
            print(f"Progress: {i+1}/{total}")

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)

    print(f"\nSaved to {output_csv}")
    return df

def build_similarity__batched_csv(
    output="shape_similarity.csv",
    size=192,
    steps=90,
    batch_size=128,
    angle_chunk=16
):
    world, states = load_datasets()
    tensors = {}
    types = {}

    # Countries
    for name in world["ADMIN"]:
        geom = normalize(largest_part(world[world["ADMIN"] == name].geometry.values[0]))
        img = rasterize(geom, size)

        tensors[name] = torch.tensor(img).unsqueeze(0).unsqueeze(0).to(device)
        types[name] = "country"

    # States
    for name in states["name"]:
        geom = normalize(largest_part(states[states["name"] == name].geometry.values[0]))
        img = rasterize(geom, size)

        key = "Georgia (state)" if name == "Georgia" else name

        tensors[key] = torch.tensor(img).unsqueeze(0).unsqueeze(0).to(device)
        types[key] = "state"

    names = list(tensors.keys())
    pairs = list(combinations(names, 2))
    angles = torch.linspace(0, np.pi, steps, device=device)

    results = []

    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]

        t1 = torch.cat([tensors[a] for a, _ in batch])
        t2 = torch.cat([tensors[b] for _, b in batch])

        vals, idx = compute_iou_rotation_invariant(t1, t2, angles, angle_chunk)

        for j, (a, b) in enumerate(batch):
            results.append({
                "shape1": a,
                "type1": types[a],
                "shape2": b,
                "type2": types[b],
                "iou": vals[j].item(),
                "angle": angles[idx[j]].item()
            })

        print(f"{i}/{len(pairs)}")

    df = pd.DataFrame(results)
    df.to_csv(output, index=False)

    return df


# ========================
# SEARCH
# ========================

def search(name, csv_file="shape_similarity.csv", top_k=5, mode="all"):
    """
    Search similar shapes.

    Args:
        name: query shape
        mode:
            "all"      → everything
            "states"   → only US states
            "countries"→ only countries
    """

    df = pd.read_csv(csv_file)

    df_rev = df.rename(columns={
        "shape1": "shape2",
        "shape2": "shape1",
        "type1": "type2",
        "type2": "type1"
    })

    df_all = pd.concat([df, df_rev], ignore_index=True)

    results = df_all[df_all["shape1"] == name]

    if mode == "states":
        results = results[results["type2"] == "state"]
    elif mode == "countries":
        results = results[results["type2"] == "country"]

    return results.sort_values("iou", ascending=False).head(top_k)

def country_to_states_from_csv(country_name, csv_file="shape_similarity.csv", top_k=None):
    """
    Get similarity of a country vs all US states using existing CSV.

    Args:
        country_name (str): Name of country (must match CSV)
        csv_file (str): Path to similarity CSV
        top_k (int or None): number of results to return (None = all)

    Returns:
        pandas DataFrame sorted by IoU
    """

    import pandas as pd

    df = pd.read_csv(csv_file)

    # Flip pairs so country can appear on left side
    df_rev = df.rename(columns={
        "shape1": "shape2",
        "shape2": "shape1",
        "type1": "type2",
        "type2": "type1"
    })

    df_all = pd.concat([df, df_rev], ignore_index=True)

    # Filter: country vs states only
    results = df_all[
        (df_all["shape1"] == country_name) &
        (df_all["type2"] == "state")
    ]

    results = results.sort_values("iou", ascending=False)

    if top_k:
        results = results.head(top_k)

    return results
def top_k_similar_places(csv_file="shape_similarity.csv", k=3):
    """
    For each place, return its top K most similar shapes.

    Args:
        csv_file (str): path to similarity CSV
        k (int): number of top matches per country

    Returns:
        pandas DataFrame
    """
    import pandas as pd

    df = pd.read_csv(csv_file)

    # Make symmetric (A→B and B→A)
    df_rev = df.rename(columns={
        "shape1": "shape2",
        "shape2": "shape1",
        "type1": "type2",
        "type2": "type1"
    })

    df_all = pd.concat([df, df_rev], ignore_index=True)


    # Sort by IoU descending per country
    df_all = df_all.sort_values(["shape1", "iou"], ascending=[True, False])

    # Take top K per country
    result = df_all.groupby("shape1").head(k)

    return result
def count_shape2_from_topk(csv_file="shape_similarity.csv", k=3):
    """
    Count how often each place appears in the top-K matches
    of all other places.

    Args:
        csv_file (str): path to similarity CSV
        k (int): number of top matches per place

    Returns:
        pandas DataFrame with counts
    """
    import pandas as pd

    # get top-k per place
    topk = top_k_similar_places(csv_file, k)

    # count appearances of shape2
    counts = (
        topk["shape2"]
        .value_counts()
        .reset_index()
    )

    counts.columns = ["place", "count"]

    return counts