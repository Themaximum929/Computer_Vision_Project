# Training Data Preprocessing & Text Styling Guide

## Overview

This guide covers two key improvements:
1. **Preprocessing training data** - Remove text from posters before LoRA training
2. **Genre-based text styling** - Add styled titles that match poster genres

---

## 1. Preprocessing Training Data

### Why Preprocess?

Before training LoRA on poster images, we need to remove existing text to:
- Prevent the model from learning to generate artificial text
- Focus training on visual composition and style
- Improve quality of generated posters

### How to Preprocess

#### Step 1: Collect Raw Posters
```bash
python src/collect_data.py
```
This saves raw posters to `data/posters/`

#### Step 2: Preprocess (Remove Text)
```bash
python preprocess_training_data.py --input data/posters --output data/posters_clean
```

**Options:**
- `--input`: Directory with raw posters (default: `data/posters`)
- `--output`: Directory for cleaned posters (default: `data/posters_clean`)
- `--iterations`: Text removal passes (default: 3, more = cleaner)

**Example:**
```bash
# Aggressive cleaning (5 passes)
python preprocess_training_data.py --iterations 5

# Custom directories
python preprocess_training_data.py --input data/raw --output data/clean
```

#### Step 3: Train LoRA on Clean Data
```bash
python src/train_lora.py --data-dir data/posters_clean --output models/poster_lora
```

### Complete Workflow

```bash
# 1. Collect posters
python src/collect_data.py

# 2. Clean posters (remove text)
python preprocess_training_data.py

# 3. Train LoRA on clean data
python src/train_lora.py --data-dir data/posters_clean

# 4. Generate posters with trained model
python run_pipeline.py "space adventure" --lora
```

---

## 2. Genre-Based Text Styling

### Available Styles

The system includes 9 genre-specific text styles:

| Genre | Font Style | Color | Effects |
|-------|-----------|-------|---------|
| **Action** | Bold Impact | Red (255,50,50) | Heavy stroke, large shadow |
| **Horror** | Impact | Dark Red (200,0,0) | Large shadow, centered |
| **Sci-Fi** | Clean Arial | Cyan (100,200,255) | Glowing effect, wide spacing |
| **Drama** | Elegant Times | White | Subtle shadow, refined |
| **Comedy** | Playful Comic | Yellow (255,220,0) | Orange stroke, top position |
| **Thriller** | Arial | White | Dark shadow, suspenseful |
| **Fantasy** | Times | Gold (255,215,0) | Brown stroke, magical feel |
| **Romance** | Times | Pink (255,182,193) | Soft shadow, delicate |
| **Cinematic** | Arial | White | Balanced, professional |

### How Text Styling Works

#### Automatic Genre Detection
When using `genre_lora=True`, the system:
1. Detects genre from keywords
2. Loads genre-specific LoRA
3. Applies matching text style

```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(
    genre_lora=True,      # Enable genre detection
    add_title=True        # Enable text overlay
)

# Genre auto-detected, style auto-applied
image, brief, metrics = pipeline.generate_poster("dark horror mansion")
# -> Uses horror style (dark red, large shadow, centered)
```

#### Manual Style Selection
```python
from src.text_overlay import TextOverlay
from PIL import Image

overlay = TextOverlay()
image = Image.open("poster.png")

# Use specific genre style
styled = overlay.add_title(image, "SPACE ODYSSEY", genre="scifi")

# Or use named style
styled = overlay.add_title(image, "LOVE STORY", style="romance")
```

### Customizing Styles

Edit `src/poster_text_styles.py`:

```python
POSTER_STYLES = {
    "custom": {
        "font": "impact.ttf",           # Font file
        "fallback": "arial.ttf",        # Fallback font
        "size_ratio": 0.10,             # 10% of image height
        "color": (255, 255, 255),       # RGB color
        "stroke_width": 2,              # Outline thickness
        "stroke_color": (0, 0, 0),      # Outline color
        "shadow_offset": 4,             # Shadow distance
        "shadow_color": (0, 0, 0, 180), # RGBA shadow
        "position": "bottom",           # top/center/bottom
        "letter_spacing": 5             # Space between letters
    }
}
```

### Style Parameters Explained

- **font**: Primary font file (Windows fonts in `C:\Windows\Fonts\`)
- **fallback**: Backup font if primary not found
- **size_ratio**: Text size as fraction of image height (0.08 = 8%)
- **color**: RGB tuple for text color
- **stroke_width**: Outline thickness (0 = no outline)
- **stroke_color**: RGB color for outline
- **shadow_offset**: Pixels to offset shadow
- **shadow_color**: RGBA tuple (last value = opacity)
- **position**: Vertical placement (top/center/bottom)
- **letter_spacing**: Extra space between letters

---

## Examples

### Example 1: Full Pipeline with Preprocessing

```bash
# Collect 50 action posters
python src/collect_data.py --genre action --count 50

# Clean them
python preprocess_training_data.py --input data/posters --output data/action_clean

# Train action LoRA
python src/train_lora.py --data-dir data/action_clean --output models/lora_action

# Generate with action style
python run_pipeline.py "explosive car chase" --genre-lora --add-title
```

### Example 2: Custom Text Styling

```python
from src.pipeline import Key2PosterPipeline

# Generate with specific genre
pipeline = Key2PosterPipeline(
    baseline_style=True,
    add_title=True
)

# Horror poster with horror text style
image, _, _ = pipeline.generate_poster("haunted mansion ghost")

# The text will automatically use horror styling:
# - Dark red color
# - Large shadow
# - Centered position
```

### Example 3: Batch Processing with Styles

```python
from src.text_overlay import TextOverlay
from PIL import Image
from pathlib import Path

overlay = TextOverlay()

posters = [
    ("action_poster.png", "EXPLOSIVE ACTION", "action"),
    ("horror_poster.png", "DARK TERROR", "horror"),
    ("scifi_poster.png", "SPACE ODYSSEY", "scifi")
]

for img_path, title, genre in posters:
    image = Image.open(img_path)
    styled = overlay.add_title(image, title, genre=genre)
    styled.save(f"styled_{img_path}")
```

---

## Tips & Best Practices

### Preprocessing
- Use 3-5 iterations for best results
- More iterations = cleaner but may remove some details
- Check output quality before training
- Keep original data as backup

### Text Styling
- Match text style to poster genre for consistency
- Use bold styles (action, horror) for dramatic posters
- Use elegant styles (drama, romance) for subtle posters
- Adjust `size_ratio` if text is too large/small
- Increase `shadow_offset` for better readability on busy backgrounds

### Font Availability
Common Windows fonts:
- `arial.ttf` - Clean, modern
- `arialbd.ttf` - Bold Arial
- `times.ttf` - Elegant serif
- `impact.ttf` - Bold, impactful
- `comic.ttf` - Playful

If font not found, system uses fallback automatically.

---

## Troubleshooting

**Text removal too aggressive:**
```bash
python preprocess_training_data.py --iterations 2
```

**Text too small:**
Edit `src/poster_text_styles.py`, increase `size_ratio` to 0.12

**Text hard to read:**
Increase `shadow_offset` and `stroke_width` in style config

**Font not found:**
Use `arial.ttf` or `times.ttf` (always available on Windows)

---

## Summary

**Before training:**
```bash
python preprocess_training_data.py
```

**Generate with styled text:**
```bash
python run_pipeline.py "your keywords" --genre-lora --add-title
```

**Result:** Clean training data + Genre-matched text styling = Professional posters!
