# Complete Preprocessing Workflow

## Overview

This workflow shows how genre information flows from scraping → preprocessing → training.

---

## Step-by-Step Process

### Step 1: Scrape Posters with Genre Labels

**Script:** `src/collect_data.py`

```bash
python src/collect_data.py
```

**What it does:**
- Scrapes movie posters from IMDB
- Extracts genre information (action, horror, sci-fi, etc.)
- Saves with genre prefix: `action_adventure_tt0468569.jpg`
- Creates `metadata.json` with genre mappings

**Output:**
```
data/posters/
├── action_adventure_tt0468569.jpg
├── horror_thriller_tt0081505.jpg
├── scifi_action_tt0816692.jpg
└── metadata.json
```

**metadata.json format:**
```json
[
  {
    "id": "tt0468569",
    "genres": ["action", "adventure", "drama"],
    "path": "data/posters/action_adventure_tt0468569.jpg"
  }
]
```

---

### Step 2: Preprocess Posters (Remove Text)

**Script:** `preprocess_training_data.py`

```bash
python preprocess_training_data.py --input data/posters --output data/posters_clean
```

**What it does:**
- Removes text from all posters (3-pass aggressive detection)
- **Preserves original filenames** (keeps genre info)
- Copies `metadata.json` to output directory
- Shows genre distribution

**Output:**
```
data/posters_clean/
├── action_adventure_tt0468569.jpg  (text removed)
├── horror_thriller_tt0081505.jpg   (text removed)
├── scifi_action_tt0816692.jpg      (text removed)
└── metadata.json                   (copied)
```

**Key:** Filenames still contain genre information!

---

### Step 3: Train Genre-Specific LoRAs

**Script:** `train_by_genre.py`

```bash
python train_by_genre.py --data-dir data/posters_clean --epochs 20
```

**What it does:**
- Reads `metadata.json` to get genre mappings
- Groups posters by primary genre
- Trains separate LoRA for each genre (if >= 10 images)
- Saves to `models/lora_{genre}/`

**Output:**
```
models/
├── lora_action/
│   └── lora_weights.pth
├── lora_horror/
│   └── lora_weights.pth
├── lora_scifi/
│   └── lora_weights.pth
└── ...
```

---

## Complete Workflow Commands

```bash
# 1. Scrape posters with genres
python src/collect_data.py

# 2. Remove text (preserves genre info)
python preprocess_training_data.py

# 3. Train genre-specific LoRAs
python train_by_genre.py

# 4. Generate with genre detection
python run_pipeline.py "space adventure" --genre-lora --add-title
```

---

## How Genre Information Flows

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Scraping (src/collect_data.py)                     │
├─────────────────────────────────────────────────────────────┤
│ IMDB → Extract genres → Save as "genre_id.jpg"             │
│ Output: action_adventure_tt0468569.jpg + metadata.json     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Preprocessing (preprocess_training_data.py)        │
├─────────────────────────────────────────────────────────────┤
│ Remove text → Keep filename → Copy metadata.json           │
│ Output: action_adventure_tt0468569.jpg (clean)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Training (train_by_genre.py)                       │
├─────────────────────────────────────────────────────────────┤
│ Read metadata.json → Group by genre → Train LoRAs          │
│ Output: models/lora_action/, models/lora_horror/, etc.     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Generation (run_pipeline.py --genre-lora)          │
├─────────────────────────────────────────────────────────────┤
│ Detect genre → Load matching LoRA → Apply genre style      │
│ Output: Professional poster with genre-matched styling     │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/scraper.py` | Scrapes IMDB, extracts genres |
| `src/collect_data.py` | Main scraping script |
| `preprocess_training_data.py` | Removes text, preserves genres |
| `train_by_genre.py` | Trains genre-specific LoRAs |
| `metadata.json` | Genre mappings (created by scraper) |

---

## Example: Action Genre Flow

```bash
# 1. Scrape action movies
python src/collect_data.py
# → Creates: action_adventure_tt0468569.jpg

# 2. Remove text
python preprocess_training_data.py
# → Creates: action_adventure_tt0468569.jpg (clean, same name)

# 3. Train action LoRA
python train_by_genre.py
# → Reads metadata.json
# → Finds all "action" posters
# → Trains models/lora_action/

# 4. Generate action poster
python run_pipeline.py "explosive car chase" --genre-lora --add-title
# → Detects "action" genre
# → Loads models/lora_action/
# → Applies action text style (bold red)
```

---

## Options

### Preprocessing Options
```bash
# More aggressive text removal
python preprocess_training_data.py --iterations 5

# Custom directories
python preprocess_training_data.py --input data/raw --output data/clean
```

### Training Options
```bash
# Require more images per genre
python train_by_genre.py --min-images 20

# More training epochs
python train_by_genre.py --epochs 30

# Custom output directory
python train_by_genre.py --output my_models
```

---

## Summary

**The key insight:** Genre information is preserved through filenames and metadata.json throughout the entire pipeline, enabling genre-specific training and styling.

1. **Scraper** adds genre to filename: `action_adventure_tt0468569.jpg`
2. **Preprocessor** keeps filename: `action_adventure_tt0468569.jpg` (text removed)
3. **Trainer** reads metadata, groups by genre, trains separate LoRAs
4. **Generator** detects genre, loads matching LoRA, applies matching style

**Result:** Professional posters with genre-appropriate visual style and text styling!
