"""
Geography Game Utilities (Powered by Shape Similarity CSV)

Uses:
    - shape_similarity.csv (from your engine)

Provides game mechanics:
    - Match questions
    - Higher/lower comparisons
    - Guess validation
    - Odd-one-out
    - Ranking challenges
    - Daily challenge

All functions are lightweight and CSV-based (fast).
"""

import pandas as pd
import random

US_STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia (state)",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
    "District of Columbia"
]

EUROPE = [
    "Albania",
    "Austria",
    "Belarus",
    "Belgium",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Kosovo",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Moldova",
    "Montenegro",
    "Netherlands",
    "North Macedonia",
    "Norway",
    "Poland",
    "Portugal",
    "Republic of Serbia",
    "Romania",
    "Russia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "Turkey",
    "Ukraine",
    "United Kingdom"
]

AFRICA = [
    "Algeria",
    "Angola",
    "Benin",
    "Botswana",
    "Burkina Faso",
    "Burundi",
    "Cameroon",
    "Central African Republic",
    "Chad",
    "Democratic Republic of the Congo",
    "Djibouti",
    "Egypt",
    "Equatorial Guinea",
    "Eritrea",
    "Ethiopia",
    "Gabon",
    "Gambia",
    "Ghana",
    "Guinea",
    "Guinea-Bissau",
    "Ivory Coast",
    "Kenya",
    "Lesotho",
    "Liberia",
    "Libya",
    "Madagascar",
    "Malawi",
    "Mali",
    "Mauritania",
    "Morocco",
    "Mozambique",
    "Namibia",
    "Niger",
    "Nigeria",
    "Republic of the Congo",
    "Rwanda",
    "Senegal",
    "Sierra Leone",
    "Somalia",
    "Somaliland",
    "South Africa",
    "South Sudan",
    "Sudan",
    "Togo",
    "Tunisia",
    "Uganda",
    "United Republic of Tanzania",
    "Western Sahara",
    "Zambia",
    "Zimbabwe",
    "eSwatini"
]

ASIA = [
    "Afghanistan",
    "Armenia",
    "Azerbaijan",
    "Bangladesh",
    "Bhutan",
    "Brunei",
    "Cambodia",
    "China",
    "East Timor",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Israel",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kuwait",
    "Kyrgyzstan",
    "Laos",
    "Lebanon",
    "Malaysia",
    "Mongolia",
    "Myanmar",
    "Nepal",
    "North Korea",
    "Oman",
    "Pakistan",
    "Palestine",
    "Philippines",
    "Qatar",
    "Saudi Arabia",
    "South Korea",
    "Sri Lanka",
    "Syria",
    "Taiwan",
    "Tajikistan",
    "Thailand",
    "Turkey",
    "Turkmenistan",
    "United Arab Emirates",
    "Uzbekistan",
    "Vietnam",
    "Yemen"
]

NORTH_AMERICA = [
    "Belize",
    "Canada",
    "Costa Rica",
    "Cuba",
    "Dominican Republic",
    "El Salvador",
    "Greenland",
    "Guatemala",
    "Haiti",
    "Honduras",
    "Jamaica",
    "Mexico",
    "Nicaragua",
    "Panama",
    "Puerto Rico",
    "The Bahamas",
    "Trinidad and Tobago",
    "United States of America"
]

SOUTH_AMERICA = [
    "Argentina",
    "Bolivia",
    "Brazil",
    "Chile",
    "Colombia",
    "Ecuador",
    "Falkland Islands",
    "Guyana",
    "Paraguay",
    "Peru",
    "Suriname",
    "Uruguay",
    "Venezuela"
]

OCEANIA = [
    "Australia",
    "Fiji",
    "New Caledonia",
    "New Zealand",
    "Papua New Guinea",
    "Solomon Islands",
    "Vanuatu"
]

ISLANDS = [
    "Australia",
    "Cuba",
    "Cyprus",
    "Fiji",
    "Greenland",
    "Haiti",
    "Iceland",
    "Indonesia",
    "Ireland",
    "Jamaica",
    "Japan",
    "Madagascar",
    "New Zealand",
    "Papua New Guinea",
    "Philippines",
    "Puerto Rico",
    "Solomon Islands",
    "Sri Lanka",
    "Taiwan",
    "The Bahamas",
    "Trinidad and Tobago",
    "United Kingdom",
    "Vanuatu"
]

CATEGORIES = {
    "World": None,
    "US States": US_STATES,
    "Europe": EUROPE,
    "Africa": AFRICA,
    "Asia": ASIA,
    "North America": NORTH_AMERICA,
    "South America": SOUTH_AMERICA,
    "Oceania": OCEANIA,
    "Islands": ISLANDS
}

# ========================
# INTERNAL UTIL
# ========================

def _load_symmetric(csv_file):
    """
    Load CSV and make it symmetric (A→B and B→A).
    """
    df = pd.read_csv(csv_file)

    df_rev = df.rename(columns={
        "shape1": "shape2",
        "shape2": "shape1",
        "type1": "type2",
        "type2": "type1"
    })

    return pd.concat([df, df_rev], ignore_index=True)


# ========================
# 1. MATCH QUESTION
# ========================

def generate_match_question(csv_file="shape_similarity.csv", num_choices=4, region="World", dif_level="Easy"):
    """
    Generate a multiple-choice question:
        "Which place looks most like X?"

    Returns:
        dict with:
            - question
            - choices (list)
            - answer
    """
    
    df = _load_symmetric(csv_file)

    shapes = df["shape1"].unique().tolist()

    # filter if category provided
    if region != "World":
        shapes = [s for s in shapes if s in CATEGORIES[region]]

    if not shapes:
        raise ValueError("No valid shapes found")

    query = random.choice(shapes)

    subset = df[(df["shape1"] == query) | (df["shape2"] == query)]
    # restrict comparisons for major regions
    if region in {"US States", "Europe", "Asia", "Africa"}:
        subset = subset[
            subset["shape1"].isin(CATEGORIES[region]) &
            subset["shape2"].isin(CATEGORIES[region])
        ]
    best = subset.loc[subset["iou"].idxmax()]
    correct = best["shape1"] if best["shape2"] == query else best["shape2"]
    highest = best["iou"]
    all_shapes = subset.sort_values("iou", ascending=False)["shape2"].tolist()
    valid_shapes = [x for x in all_shapes if x not in {correct, query}]

    if(dif_level == "Easy"):
        valid_shapes = valid_shapes[len(valid_shapes)-10:]
    elif(dif_level == "Hard"):
        valid_shapes = valid_shapes[0:10]
    distractors = random.sample(
    valid_shapes,
    num_choices-1)
    

    choices = distractors + [correct]
    random.shuffle(choices)

    return {
        "base": query,
        "highest": highest,
        "choices": choices,
        "answer": correct
    }


# ========================
# 2. HIGHER / LOWER
# ========================

def get_random_pair(csv_file="shape_similarity.csv"):
    """
    Get a random pair and its IoU.

    Returns:
        (shape1, shape2, iou)
    """
    df = pd.read_csv(csv_file)
    row = df.sample(1).iloc[0]

    return row["shape1"], row["shape2"], row["iou"]


# ========================
# 3. GUESS VALIDATION
# ========================

def is_good_guess(query, guess, csv_file="shape_similarity.csv", threshold=0.5):
    """
    Check if a guessed match is "good enough".

    Args:
        query (str)
        guess (str)
        threshold (float): minimum IoU

    Returns:
        bool
    """
    df_all = _load_symmetric(csv_file)

    row = df_all[
        (df_all["shape1"] == query) &
        (df_all["shape2"] == guess)
    ]

    if row.empty:
        return False

    return row.iloc[0]["iou"] >= threshold


# ========================
# 4. ODD ONE OUT
# ========================

def odd_one_out(csv_file="shape_similarity.csv", region = "World"):
    """
    Generate an odd-one-out question.

    Returns:
        base shape,
        list of 4 choices,
        correct odd answer
    """
    df = _load_symmetric(csv_file)

    shapes = df["shape1"].unique().tolist()

    # filter if category provided
    if region != "World":
        shapes = [s for s in shapes if s in CATEGORIES[region]]

    if not shapes:
        raise ValueError("No valid shapes found")

    base = random.choice(shapes)

    """ similar = (
    df[df["shape1"] == base]
    .sort_values("iou", ascending=False)
    .head(10)["shape2"]
    .tolist()
    )
    

    all_shapes = df_all["shape2"].unique()
    odd = random.choice([x for x in all_shapes if x not in similar])

    similar = (
    df_all[df_all["shape1"] == base]
    .sort_values("iou", ascending=False)
    .head(10)["shape2"]
    .sample(3)
    .tolist()
    ) """
    similar = (
    df[
        (df["shape1"] == base) &
        (
            df["shape2"].isin(CATEGORIES[region])
            if region in {"US States", "Europe", "Asia", "Africa"}
            else True
        )
    ]
    .sort_values("iou", ascending=False)
    .head(10)["shape2"]
    .tolist()
    )
    """
    all_shapes = (
        CATEGORIES[region]
        if region in {"US States", "Europe", "Asia", "Africa"}
        else df["shape2"].unique()
    )
    """
    all_shapes = (
    df[df["shape1"] == base]["shape2"]
    .unique()
    )
    if region in {"US States", "Europe", "Asia", "Africa"}:
        all_shapes = [
            x for x in all_shapes
            if x in CATEGORIES[region]
        ]

    odd = random.choice([
        x for x in all_shapes
        if x not in similar
    ])

    similar = random.sample(similar, 3)

    choices = similar + [odd]
    random.shuffle(choices)

    odd_index = ranking = (
    df[df["shape1"] == base]
    .sort_values("iou", ascending=False)["shape2"]
    .tolist()).index(odd)+1

    return base, choices, odd, odd_index


# ========================
# 5. RANKING QUESTION
# ========================

def ranking_question(csv_file="shape_similarity.csv", k=4, region="World", dif_level="Easy"):
    """
    Generate a ranking challenge:
        "Rank these by similarity to X"

    Returns:
        base shape,
        list of options (already sorted correctly)
    """
    
    df = _load_symmetric(csv_file)

    shapes = df["shape1"].unique().tolist()

    # filter if category provided
    if region != "World":
        shapes = [s for s in shapes if s in CATEGORIES[region]]

    if not shapes:
        raise ValueError("No valid shapes found")

    base = random.choice(shapes)

    top = df[df["shape1"] == base]
    

    if region in {"US States", "Europe", "Asia", "Africa"}:
        top = top[top["shape2"].isin(CATEGORIES[region])]

    top = top.sort_values("iou", ascending=False)
    # ---------- difficulty logic ----------
    if dif_level == "Easy":
        easy = top.head(1)
        medium = pd.concat([
        top.iloc[8:12].sample(1),
        top.iloc[20:24].sample(1)])
        hard = top.iloc[34:].sample(1)

    elif dif_level == "Medium":
        easy = top.head(2)
        medium = top.iloc[2:6].sample(1)
        hard = top.iloc[6:15].sample(1)

    elif dif_level == "Hard":
        easy = top.iloc[3:5]
        medium = top.iloc[5:7].sample(1)
        hard = top.iloc[8:10].sample(1)

    else:
        raise ValueError(f"Unknown difficulty: {dif_level}")

    correct_order = pd.concat([easy, medium, hard])["shape2"].tolist()
    options = correct_order.copy()
    random.shuffle(options)

    return base, correct_order, options


# ========================
# 6. DAILY CHALLENGE
# ========================

def daily_challenge(date_seed, csv_file="shape_similarity.csv"):
    """
    Deterministic daily challenge.

    Args:
        date_seed (str or int): e.g. "2026-04-26"

    Returns:
        (shape1, shape2, iou)
    """
    random.seed(date_seed)

    df = pd.read_csv(csv_file)
    row = df.sample(1).iloc[0]

    return row["shape1"], row["shape2"], row["iou"]


# ========================
# 7. TOP-K MATCHES (HELPER)
# ========================

def top_k_matches(name, csv_file="shape_similarity.csv", k=5):
    """
    Get top K matches for a shape.

    Returns:
        DataFrame sorted by IoU
    """
    df_all = _load_symmetric(csv_file)

    return df_all[df_all["shape1"] == name] \
        .sort_values("iou", ascending=False) \
        .head(k)

def swipe_pair(csv_file="shape_similarity.csv", country1="random", percent=0.25, region = "World"):
    """
    Generate a swipe pair.

    Returns:
        (shape1, shape2, iou, top_per)

    top_per = True if shape2 is in top X% most similar to shape1

    Balanced:
        ~50% True / ~50% False
    Supports:
        - random start
        - chain mode (A → B → C)
    """

    df = _load_symmetric(csv_file)

    shapes = df["shape1"].unique().tolist()

    # filter if category provided
    if region != "World":
        shapes = [s for s in shapes if s in CATEGORIES[region]]

    if not shapes:
        raise ValueError("No valid shapes found")

    # -----------------------
    # PICK BASE SHAPE
    # -----------------------
    if country1 == "random":

        base = random.choice(shapes)
    else:
        base = country1

    # -----------------------
    # GET ALL MATCHES
    # -----------------------

    subset = df[
    (df["shape1"] == base) |
    (df["shape2"] == base)
    ].copy()

    if region in {"US States", "Europe", "Asia", "Africa"}:
        subset = subset[
            subset["shape1"].isin(CATEGORIES[region]) &
            subset["shape2"].isin(CATEGORIES[region])
        ]

    # fallback safety
    if subset.empty:
        row = df.sample(1).iloc[0]
        return row["shape1"], row["shape2"], row["iou"], False

    # normalize so base is always first
    subset["other"] = subset.apply(
        lambda r: r["shape2"] if r["shape1"] == base else r["shape1"],
        axis=1
    )

    subset = subset.sort_values("iou", ascending=False)

    # -----------------------
    # SPLIT TOP % vs REST
    # -----------------------
    cutoff = max(1, int(len(subset) * percent))

    top_df = subset.head(cutoff)
    rest_df = subset.iloc[cutoff:]

    # -----------------------
    # BALANCED TRUE / FALSE
    # -----------------------
    if random.random() < 0.5 and not top_df.empty:
        row = top_df.sample(1).iloc[0]
        top_per = True
    else:
        if not rest_df.empty:
            row = rest_df.sample(1).iloc[0]
            top_per = False
        else:
            # fallback if no "rest"
            row = top_df.sample(1).iloc[0]
            top_per = True

    a = base
    b = row["other"]
    iou = row["iou"]

    return a, b, iou, top_per

def choose_place(csv_file="shape_similarity.csv", region="World"):
    df = _load_symmetric(csv_file)

    shapes = df["shape1"].unique().tolist()

    # filter if category provided
    if region != "World":
        shapes = [s for s in shapes if s in CATEGORIES[region]]

    if not shapes:
        raise ValueError("No valid shapes found")

    return random.choice(shapes)