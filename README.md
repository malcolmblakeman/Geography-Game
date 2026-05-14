# Geography Game 🌍

An interactive geography guessing game built with Streamlit that challenges players to recognize countries, states, and regions using visual similarity between flags and geographic outlines.

This project combines image similarity, geography knowledge, pattern recognition, and spatial reasoning into a collection of fast-paced mini-games. Players can test themselves on national flags, country shapes, U.S. state outlines, island geography, and more through several unique gameplay modes.

---
## Visual Data Sources

### 🚩 Flags
- [hayleyox/flags GitHub Repository](https://github.com/hjnilsson/country-flags)

### 🌍 Geographic Outlines
- [Natural Earth Data](https://www.naturalearthdata.com)
- [PublicaMundi US States GeoJSON Dataset](https://github.com/PublicaMundi/MappingAPI/tree/master/data/geojson)

---
# Features

## Two Core Game Types

### 🚩 Flag Mode

Guess locations based on visual similarity between flags.

The game compares flags using:

* Color similarity
* Stripe/layout structure
* Symbol placement
* Overall visual composition

Examples:

* Romania vs Chad
* Indonesia vs Monaco
* Nordic cross flags
* Pan-Arab color schemes

This mode rewards strong visual memory and pattern recognition.

---

### 🌍 Outline Mode

Guess locations based on geographic shape similarity.

This mode compares geographic outlines using:

* Shape overlap
* Rotation matching
* Spatial similarity
* IoU (Intersection over Union) style comparisons

Examples:

* Italy vs New Zealand
* Cuba vs Croatia
* Chile vs Vietnam
* Similar island chains and coastlines

Players can rotate outlines in several modes, making spatial reasoning an important part of gameplay.

---

# Regions

The game supports multiple geography pools:

* World
* U.S. States
* Europe
* Africa
* Asia
* North America
* South America
* Oceania
* Islands

This allows players to focus on specific regions or play globally.

---

# Difficulty Levels

Most game modes support multiple difficulty levels:

## Easy

* Larger similarity gaps
* More obvious answers
* Easier visual distinctions

## Medium

* Moderately similar choices
* Requires stronger geographic intuition

## Hard

* Extremely close comparisons
* Subtle differences
* Designed for geography enthusiasts

---

# Game Modes

The project contains multiple unique game modes, each emphasizing different geography skills.

---

# 1. Match Question

## Objective

Choose which option looks most visually similar to the target location.

The player is shown:

* A target flag or outline
* Multiple possible answers

Example:

> “What looks most like Nepal?”

Players then choose from several visually similar options.

---

## Features

* Multiple choice gameplay
* Shape rotation support
* Difficulty scaling
* Randomized answer choices
* Similarity score calculations
---

## Skills Tested

* Visual pattern recognition
* Geography familiarity
* Shape memory
* Flag color/layout recognition

---

# 2. Higher / Lower

## Objective

Determine whether one pair is more visually similar than another pair.

Example:

Pair A:

* Romania vs Chad

Pair B:

* France vs Netherlands

Question:

> Is Pair B more similar or less similar than Pair A?

---

## Features

* Relative comparison gameplay
* Similarity ranking intuition
* Difficulty scaling based on closeness
* Randomized pair generation

---

## Skills Tested

* Comparative reasoning
* Understanding subtle visual differences
* Similarity estimation

---

# 3. Odd One Out

## Objective

Find the location that does not visually belong with the others.

The player is shown:

* A reference location
* Several similar choices
* One intentionally different option

Example:

A set of Scandinavian-style flags with one unrelated flag.

---

## Features

* Cluster-based similarity gameplay
* Randomized odd-item generation
* Shape and flag support

---

## Skills Tested

* Pattern grouping
* Outlier detection
* Regional visual familiarity

---

# 4. Ranking Mode

## Objective

Rank several locations from most similar to least similar relative to a target.

Players drag and reorder items into the correct similarity order.

---

## Features

* Drag-and-drop interface
* Multi-attempt gameplay
* Partial correctness feedback
* Progressive difficulty

---

## Example

Target:

> Japan

Possible rankings:

* Philippines
* Indonesia
* Madagascar
* Iceland

Players must determine which outlines or flags are visually closest.

---

## Skills Tested

* Fine-grained visual comparison
* Ordering and ranking intuition
* Multi-item reasoning

---

# 5. Swipe Mode

## Objective

Quickly decide whether two locations are visually similar.

Players respond with:

* 👍 Similar
* 👎 Not Similar

The mode is inspired by fast swipe-style mobile games.

---

## Features

* Fast-paced gameplay
* Binary decisions
* Percentile-based similarity thresholds
* Difficulty scaling

---

## Skills Tested

* Fast visual judgment
* Intuition for similarity
* Rapid recognition

---

# 6. Blur Reveal

## Objective

Guess the location while the image is heavily blurred.

Each incorrect guess reduces the blur slightly.

Players gradually receive more visual information with each attempt.

---

## Features

* Progressive reveal mechanics
* Dynamic blur reduction
* Guess suggestions/autocomplete
* Attempts tracking

---

## Example

A blurred flag slowly becomes recognizable after several incorrect guesses.

---

## Skills Tested

* Partial information reasoning
* Shape/color recognition
* Deduction under uncertainty

---

# 7. Rotate Game

## Objective

Rotate a shape back to its correct geographic orientation.

Players use a rotation slider to align the outline properly.

---

## Features

* Rotation mechanics
* Tolerance-based scoring
* Difficulty scaling by angle precision
* Spatial reasoning gameplay

---

## Example

A rotated outline of Italy or Vietnam must be aligned correctly.

---

## Skills Tested

* Spatial awareness
* Mental rotation ability
* Geographic orientation knowledge

---

# 8. Daily Challenge

## Objective

Guess the similarity score between two locations.

The challenge changes daily and is deterministic based on the current date.

---

## Features

* Daily replayable puzzle
* Shared daily challenge for all players
* Attempts tracking
* Similarity score guessing

---

## Skills Tested

* Similarity estimation
* Geographic intuition
* Long-term improvement

---

# Technical Details

## Built With

* Python
* Streamlit
* Pandas
* HTML/CSS rendering inside Streamlit
* SVG rendering for outlines

---

## Image Handling

### Outline Rendering

Country and state outlines are rendered using SVG files.

Features include:

* Rotation
* Blur effects
* Dynamic scaling
* Simplified rendering

---

### Flag Rendering

Flags are rendered from PNG assets.

Features include:

* Rotation
* Blur mechanics
* Responsive sizing
* Base64 embedding for browser display

---

# Similarity Systems

## Flag Similarity

Flag similarity is based on visual appearance and layout structure.

Examples of similarity categories:

* Shared colors
* Shared stripe layouts
* Shared symbolic structures
* Shared historical design styles

---

## Shape Similarity

Shape similarity is based on geographic outline overlap.

The project uses methods inspired by:

* Shape matching
* Intersection-over-Union (IoU)
* Rotation-based alignment
* Polygon similarity techniques

---

# Educational Value

The game is designed to improve:

* Geographic knowledge
* Flag recognition
* Spatial reasoning
* Pattern recognition
* Comparative visual analysis
* Regional familiarity

It works well both as:

* A casual geography game
* A geography learning tool
* A classroom activity
* A challenge for geography enthusiasts

---

# Running Locally

## Install Requirements

```bash
pip install -r requirements.txt
```

---

## Launch Streamlit

```bash
streamlit run app.py
```

---


# Future Ideas

Please feel free to add your own game modes and espcially game types, I am working on more similar visual games.
---

# Why This Project Exists

Most geography games focus on memorization.

This project instead focuses on:

* visual similarity
* intuition
* spatial reasoning
* comparative recognition

It encourages players to think about geography in a more visual and structural way.

---

# License

This project is open-source and intended for educational and entertainment purposes.

---

# Acknowledgments

Inspired by:

* Geography quizzes
* Visual reasoning games
* Flag identification communities
* Spatial puzzle games
* Shape matching algorithms

---

Enjoy exploring geography through visual similarity! 🌎
