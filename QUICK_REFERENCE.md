# Quick Reference Guide

## Two New Features

### 1. Preprocess Training Data (Remove Text)
```bash
python preprocess_training_data.py
```

### 2. Genre-Based Text Styling (Automatic)
```bash
python run_pipeline.py "keywords" --genre-lora --add-title
```

---

## Complete Workflow

```bash
# Step 1: Collect posters
python src/collect_data.py

# Step 2: Clean posters (NEW!)
python preprocess_training_data.py

# Step 3: Train LoRA on clean data
python src/train_lora.py --data-dir data/posters_clean

# Step 4: Generate with styled text (NEW!)
python run_pipeline.py "space adventure" --genre-lora --add-title
```

---

## Commands

### Preprocessing
```bash
# Basic (default settings)
python preprocess_training_data.py

# Custom directories
python preprocess_training_data.py --input data/raw --output data/clean

# More aggressive cleaning
python preprocess_training_data.py --iterations 5
```

### Generation with Styling
```bash
# Auto-detect genre + apply matching style
python run_pipeline.py "dark horror" --genre-lora --add-title

# Baseline + generic cinematic style
python run_pipeline.py "space adventure" --baseline-style --add-title

# Fast generation (no text removal, no super-res)
python run_pipeline.py "action hero" --genre-lora --add-title --no-text-removal
```

### Test Styles
```bash
# Generate samples of all 9 styles
python test_text_styles.py
```

---

## Available Text Styles

| Genre | Color | Effect |
|-------|-------|--------|
| action | Red | Bold, heavy stroke |
| horror | Dark Red | Large shadow, centered |
| scifi | Cyan | Glowing, wide spacing |
| drama | White | Elegant, subtle |
| comedy | Yellow | Playful, top position |
| thriller | White | Dark shadow |
| fantasy | Gold | Magical, brown stroke |
| romance | Pink | Soft, delicate |
| cinematic | White | Professional, balanced |

---

## Python API

### Preprocessing
```python
from pathlib import Path
from PIL import Image
from src.aggressive_text_remover import AggressiveTextRemover

remover = AggressiveTextRemover()
image = Image.open("poster.jpg")
clean_image, found = remover.remove_text(image, iterations=3)
clean_image.save("clean_poster.jpg")
```

### Text Styling
```python
from src.text_overlay import TextOverlay
from PIL import Image

overlay = TextOverlay()
image = Image.open("poster.png")

# Use genre style
styled = overlay.add_title(image, "MOVIE TITLE", genre="action")

# Use named style
styled = overlay.add_title(image, "MOVIE TITLE", style="cinematic")

styled.save("styled_poster.png")
```

### Full Pipeline
```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(
    genre_lora=True,      # Auto-detect genre
    add_title=True,       # Add styled text
    aggressive_text_removal=True,
    super_resolution=True
)

image, brief, metrics = pipeline.generate_poster(
    "space exploration adventure",
    output_path="outputs/poster.png",
    seed=42
)
```

---

## File Locations

### Input/Output
- Raw posters: `data/posters/`
- Clean posters: `data/posters_clean/`
- Generated posters: `outputs/`
- Style tests: `outputs/text_style_tests/`

### Configuration
- Text styles: `src/poster_text_styles.py`
- Pipeline: `src/pipeline.py`
- Text overlay: `src/text_overlay.py`

### Scripts
- Preprocess: `preprocess_training_data.py`
- Test styles: `test_text_styles.py`
- Generate: `run_pipeline.py`
- Web UI: `app.py` or `app_simple.py`

---

## Customization

### Edit Text Style
`src/poster_text_styles.py`:
```python
"mystyle": {
    "font": "impact.ttf",
    "size_ratio": 0.10,        # 10% of height
    "color": (255, 255, 255),  # White
    "stroke_width": 2,
    "shadow_offset": 4,
    "position": "bottom"       # top/center/bottom
}
```

### Use Custom Style
```python
overlay.add_title(image, "TITLE", style="mystyle")
```

---

## Tips

### Preprocessing
- Use 3 iterations for balance
- Use 5 iterations for maximum cleaning
- Check output before training
- Keep originals as backup

### Text Styling
- Genre detection works best with clear keywords
- Increase `size_ratio` if text too small
- Increase `shadow_offset` for better readability
- Use `position="center"` for dramatic effect

---

## Troubleshooting

**Text removal too aggressive:**
```bash
python preprocess_training_data.py --iterations 2
```

**Text too small:**
Edit `size_ratio` in `src/poster_text_styles.py`

**Font not found:**
System automatically uses fallback (arial.ttf)

**Genre not detected:**
Use more specific keywords or manual style selection

---

## Documentation

- `PREPROCESSING_GUIDE.md` - Detailed guide
- `IMPROVEMENTS_SUMMARY.md` - Feature overview
- `README.md` - Main documentation
- `QUICK_REFERENCE.md` - This file
