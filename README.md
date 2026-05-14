# Geography Game 🌍

An interactive geography guessing game built with Streamlit that challenges players to recognize countries, states, and regions using visual similarity between flags and geographic outlines.

This project combines image similarity, geography knowledge, pattern recognition, and spatial reasoning into a collection of fast-paced mini-games. Players can test themselves on national flags, country shapes, U.S. state outlines, island geography, and more through several unique gameplay modes.

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
