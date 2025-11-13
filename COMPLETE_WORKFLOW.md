# Complete Workflow: Genre-Specific LoRA Training

## Step-by-Step Guide

### Step 1: Collect Poster Data (if not already done)

```bash
python src/collect_data.py
```

**What it does:**
- Scrapes 50+ movie posters from IMDB
- Saves to `data/posters/`
- Creates `metadata.json` with genres

**Output:**
```
data/posters/
├── action_epic_tt0468569.jpg
├── scifi_space_tt0076759.jpg
├── fantasy_animation_tt0245429.jpg
├── ...
└── metadata.json
```

### Step 2: Organize by Genre

```bash
python organize_by_genre.py
```

**What it does:**
- Reads `data/posters/metadata.json`
- Organizes posters into genre folders
- Creates genre-specific metadata

**Output:**
```
data/posters_by_genre/
├── action/
│   ├── poster1.jpg
│   ├── poster2.jpg
│   └── metadata.json
├── scifi/
│   ├── poster1.jpg
│   └── metadata.json
├── fantasy/
└── ...
```

### Step 3: Train Genre-Specific LoRAs

```bash
python train_genre_loras.py
```

**What it does:**
- Trains separate LoRA for each genre
- Saves to `models/lora_{genre}/`

**Output:**
```
models/
├── lora_action/
│   └── lora_weights.pth
├── lora_scifi/
│   └── lora_weights.pth
├── lora_fantasy/
│   └── lora_weights.pth
└── ...
```

### Step 4: Generate Posters

```bash
python app.py
```

Enable "Genre-Based LoRA" checkbox and generate!

## Quick Start

```bash
# If you already have data/posters/ with metadata.json:
python organize_by_genre.py
python train_genre_loras.py
python app.py

# If starting from scratch:
python src/collect_data.py
python organize_by_genre.py
python train_genre_loras.py
python app.py
```

## Where Poster IDs Come From

The poster IDs (IMDB IDs like tt0468569) are already in `src/scraper.py`:

```python
movie_ids = [
    "tt0468569",  # The Dark Knight
    "tt0076759",  # Star Wars
    "tt0245429",  # Spirited Away
    # ... 50+ more
]
```

These are scraped automatically when you run `python src/collect_data.py`.
