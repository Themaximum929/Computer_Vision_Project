# Genre-Specific LoRA Training Guide

## Concept

Instead of training one LoRA on all posters, train **separate LoRAs for each genre**:
- Action LoRA (trained on action posters)
- Sci-Fi LoRA (trained on sci-fi posters)
- Fantasy LoRA (trained on fantasy posters)
- etc.

When generating, **automatically detect genre** from keywords and use the matching LoRA.

## Benefits

✅ **Better Style Matching** - Each LoRA specializes in one genre  
✅ **Higher Quality** - More focused training data  
✅ **Automatic Selection** - No manual LoRA selection needed  
✅ **Scalable** - Easy to add new genres  

## Setup (3 Steps)

### Step 1: Organize Data by Genre
```bash
python organize_by_genre.py
```

**What it does:**
- Reads `data/posters/metadata.json`
- Organizes posters into genre folders
- Creates: `data/posters_by_genre/action/`, `scifi/`, `fantasy/`, etc.

**Output:**
```
data/posters_by_genre/
├── action/       (10+ posters)
├── scifi/        (8+ posters)
├── fantasy/      (12+ posters)
├── horror/       (6+ posters)
├── romance/      (5+ posters)
└── comedy/       (4+ posters)
```

### Step 2: Train Genre-Specific LoRAs
```bash
python train_genre_loras.py
```

**What it does:**
- Trains separate LoRA for each genre
- Saves to `models/lora_action/`, `models/lora_scifi/`, etc.
- Takes 10-30 minutes per genre

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

### Step 3: Use Genre-Based Generation
```bash
python app.py
# Enable "Genre-Based LoRA" checkbox
```

## How It Works

### Genre Detection
```python
Keywords: "space exploration adventure"
↓
Genre Classifier analyzes keywords
↓
Detected Genre: "scifi"
↓
Loads: models/lora_scifi/
```

### Genre Mapping
- **action**: action, battle, fight, war, combat, hero, warrior
- **scifi**: space, sci-fi, alien, robot, future, cyberpunk, galaxy
- **fantasy**: fantasy, magic, dragon, wizard, medieval, kingdom
- **horror**: horror, scary, dark, haunted, ghost, zombie, monster
- **romance**: romance, love, romantic, couple, heart, passion
- **comedy**: comedy, funny, humor, laugh, silly, fun
- **drama**: drama, emotional, serious, intense, powerful
- **thriller**: thriller, suspense, mystery, detective, crime, noir

## Usage Examples

### Example 1: Sci-Fi Poster
```bash
Keywords: "space exploration adventure"
→ Detected: scifi
→ Uses: models/lora_scifi/
→ Result: Sci-fi styled poster
```

### Example 2: Fantasy Poster
```bash
Keywords: "dark fantasy warrior"
→ Detected: fantasy
→ Uses: models/lora_fantasy/
→ Result: Fantasy styled poster
```

### Example 3: Action Poster
```bash
Keywords: "epic battle scene"
→ Detected: action
→ Uses: models/lora_action/
→ Result: Action styled poster
```

## Training Individual Genres

If you want to train just one genre:

```bash
# Train action LoRA
python src/train_lora.py --data-dir data/posters_by_genre/action --output models/lora_action

# Train scifi LoRA
python src/train_lora.py --data-dir data/posters_by_genre/scifi --output models/lora_scifi
```

## Adding New Genres

1. **Add genre keywords** to `src/genre_classifier.py`:
```python
self.genre_keywords = {
    "western": ["western", "cowboy", "frontier", "outlaw"],
    # ... other genres
}
```

2. **Organize data**:
```bash
python organize_by_genre.py
```

3. **Train LoRA**:
```bash
python src/train_lora.py --data-dir data/posters_by_genre/western --output models/lora_western
```

## Comparison

| Approach | Quality | Flexibility | Training Time |
|----------|---------|-------------|---------------|
| Single LoRA | ⭐⭐⭐ | Low | 10-30 min |
| Genre-Specific LoRAs | ⭐⭐⭐⭐⭐ | High | 60-180 min total |

## Troubleshooting

### Genre not detected correctly
**Solution:** Add more keywords to `src/genre_classifier.py`

### LoRA not found for genre
**Solution:** Train that genre's LoRA or it will fallback to baseline

### Not enough data for genre
**Solution:** Need at least 5-10 posters per genre. Collect more or merge genres.

## Performance

| Genre | Training Data | Training Time | Quality |
|-------|---------------|---------------|---------|
| Action | 10+ posters | ~15 min | ⭐⭐⭐⭐⭐ |
| Sci-Fi | 8+ posters | ~12 min | ⭐⭐⭐⭐⭐ |
| Fantasy | 12+ posters | ~18 min | ⭐⭐⭐⭐⭐ |
| Horror | 6+ posters | ~10 min | ⭐⭐⭐⭐ |

## Summary

**Quick Setup:**
```bash
# 1. Organize by genre
python organize_by_genre.py

# 2. Train all genres
python train_genre_loras.py

# 3. Use in interface
python app.py
# Enable "Genre-Based LoRA"
```

**Result:** Automatic genre detection + genre-specific styling = Better posters! 🎨
