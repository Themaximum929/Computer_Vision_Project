# Key2Poster: Creative Poster Generator

Generates professional product posters from 2-5 keywords using Stable Diffusion with LoRA fine-tuning.

**Product Categories:** Food, Fashion, Electronics, Theme Parks, Beverages, Cosmetics, Travel

## Quick Start

```bash
pip install -r requirements.txt
python app_simple.py
```
Open: **http://localhost:7860**

---

## Complete Workflow

### 1. Collect Posters
```bash
python src/collect_data.py
```
Scrapes movie posters from IMDB with genre labels → `data/posters/`

### 2. Preprocess (Remove Text)
```bash
python preprocess_training_data.py
```
Removes text from posters before training → `data/posters_clean/`

### 3. Train LoRA
```bash
python src/train_lora.py --data-dir data/posters_clean
```
Trains genre-specific LoRA models → `models/`

### 4. Generate Posters
```bash
python run_pipeline.py "space exploration adventure" --genre-lora --add-title
```
Generates poster with genre-matched styling → `outputs/`

---

## Multi-Agent System (7 Agents)

1. **Concept Expander** - Sentiment analysis + thematic expansion
2. **Genre Classifier** - Auto-detect genre from keywords
3. **Visual Designer** - Stable Diffusion v1.5 + genre-specific LoRA
4. **Text Remover** - Aggressive multi-method text detection
5. **Quality Enhancer** - Denoising + super-resolution
6. **Text Overlay** - Genre-matched styled titles (9 styles)
7. **Quality Evaluator** - Aesthetic scoring + validation

---

## Usage

### Web Interface
```bash
python app_simple.py  # Simple UI
python app.py         # Full options
```

### Command Line
```bash
# Basic generation
python run_pipeline.py "dark horror mansion"

# With genre detection + styled text
python run_pipeline.py "space adventure" --genre-lora --add-title

# With seed for reproducibility
python run_pipeline.py "cyberpunk city" --seed 42
```

### Python API
```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(
    genre_lora=True,              # Auto-detect genre
    add_title=True,               # Add styled title
    aggressive_text_removal=True,
    super_resolution=True
)

image, brief, metrics = pipeline.generate_poster(
    "space exploration adventure",
    output_path="poster.png",
    seed=42
)
```

---

## Text Styling (9 Genre Styles)

| Genre | Color | Effect |
|-------|-------|--------|
| Action | Red | Bold, heavy stroke |
| Horror | Dark Red | Large shadow, centered |
| Sci-Fi | Cyan | Glowing, wide spacing |
| Drama | White | Elegant, subtle |
| Comedy | Yellow | Playful |
| Thriller | White | Dark shadow |
| Fantasy | Gold | Magical |
| Romance | Pink | Soft, delicate |
| Cinematic | White | Professional |

Test all styles:
```bash
python test_text_styles.py
```

---

## Project Structure

```
├── src/
│   ├── pipeline.py              # Main orchestrator
│   ├── concept_expander.py      # Agent 1
│   ├── genre_classifier.py      # Agent 2
│   ├── visual_generator.py      # Agent 3
│   ├── aggressive_text_remover.py # Agent 4
│   ├── refiner.py               # Agent 5
│   ├── text_overlay.py          # Agent 6
│   ├── evaluator.py             # Agent 7
│   ├── poster_text_styles.py    # Style definitions
│   ├── scraper.py               # Data collection
│   └── lora_trainer.py          # LoRA training
├── preprocess_training_data.py  # Text removal preprocessing
├── app_simple.py                # Web UI
├── run_pipeline.py              # CLI tool
└── test_text_styles.py          # Style testing
```

---

## Key Features

✅ **Genre-Specific LoRA** - Trained on genre-labeled posters  
✅ **Automatic Genre Detection** - Matches style to content  
✅ **Text Preprocessing** - Clean training data  
✅ **9 Text Styles** - Genre-matched typography  
✅ **Aggressive Text Removal** - 3-pass detection  
✅ **Quality Enhancement** - Denoising + super-resolution  
✅ **Web Interface** - Easy to use Gradio UI  
✅ **Reproducible** - Seed-based generation

---

## Documentation

- **PREPROCESSING_GUIDE.md** - Text removal & styling guide
- **QUICK_REFERENCE.md** - Command reference
- **requirements.txt** - Dependencies

---

## Performance

| Hardware | Time |
|----------|------|
| GPU (RTX 3090) | ~10-15s |
| GPU (RTX 2060) | ~15-20s |
| CPU | ~2-3min |

---

## Summary

```bash
# Complete workflow
python src/collect_data.py                    # Collect posters
python preprocess_training_data.py            # Remove text
python src/train_lora.py --data-dir data/posters_clean  # Train
python run_pipeline.py "keywords" --genre-lora --add-title  # Generate
```

**Result:** Professional posters with genre-matched styling! 🎨
