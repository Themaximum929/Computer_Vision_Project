# Quick Start: Unified Pipeline

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Test the Unified Pipeline

```bash
python test_unified.py
```

Expected output:
```
============================================================
TESTING UNIFIED PIPELINE
============================================================

============================================================
Test 1/3: cyberpunk neon city
============================================================

🎬 UNIFIED POSTER PIPELINE
============================================================
Keywords: cyberpunk neon city

[1/5] 🧠 Analyzing Concept...
  • Sentiment: positive (0.85)
  • Mood: energetic
  • Genre: scifi

[2/5] 🎨 Generating Image...
  • Generated: (768, 1024)

[3/5] 🎨 Analyzing Colors...
  • Palette: [(120, 180, 255), (80, 40, 120), (200, 50, 150)]
  • Mood: energetic
  • Accent: (80, 40, 120)

[4/5] ✨ Processing Background...
  • Vignette applied
  • Quality enhanced

[5/5] 📝 Composing Text...
  • Template: modern
  • Text zone: bottom_center

✅ Complete in 13.2s

✅ Test 1 passed!
   Genre: scifi
   Mood: energetic
   Time: 13.2s
```

## Launch Web Interface

```bash
python app_unified.py
```

Open: **http://localhost:7860**

## Basic Usage

### Python API
```python
from src.unified_pipeline import UnifiedPosterPipeline

# Initialize
pipeline = UnifiedPosterPipeline(use_lora=True, genre_detection=True)

# Generate
result = pipeline.generate(
    keywords="cyberpunk neon city",
    template="modern",
    add_effects=True,
    seed=42
)

# Save
pipeline.save(result, "my_poster.png")

# Access results
print(f"Genre: {result['genre']}")
print(f"Mood: {result['mood']}")
print(f"Palette: {result['palette']}")
```

## Web Interface Features

1. **Keywords Input** - Enter 2-5 keywords
2. **Template Selection** - Choose from 4 styles:
   - Minimal: Clean, centered
   - Classic: Traditional bottom
   - Modern: Contemporary top-left
   - Split: Dramatic center
3. **Visual Effects** - Toggle vignette + enhancement
4. **Seed Control** - Reproducible generation
5. **Dual Preview** - Final + composition guide

## Examples

### Example 1: Cyberpunk Poster
```python
result = pipeline.generate(
    keywords="cyberpunk neon city",
    template="modern",
    add_effects=True,
    seed=42
)
```

### Example 2: Horror Poster
```python
result = pipeline.generate(
    keywords="dark horror mansion",
    template="classic",
    add_effects=True,
    seed=123
)
```

### Example 3: Space Adventure
```python
result = pipeline.generate(
    keywords="space exploration epic",
    template="minimal",
    add_effects=True,
    seed=456
)
```

## What You Get

Each generation returns:
- **Image**: Final poster (PIL Image)
- **Brief**: Sentiment, mood, themes
- **Genre**: Auto-detected genre
- **Palette**: 5 dominant colors
- **Mood**: Color-based mood
- **Time**: Generation time

Plus saved files:
- `output.png` - Final poster
- `output.json` - Metadata

## Comparison

### Original Pipeline
```bash
python app.py
# Features: LoRA, text removal, super-res
# Time: 12-15s
```

### Unified Pipeline
```bash
python app_unified.py
# Features: All above + templates + color analysis + smart composition
# Time: 13-16s (+1-2s for better quality)
```

## Tips

1. **Use seed for consistency** - Same seed = same result
2. **Try different templates** - Each has unique style
3. **Enable effects** - Vignette adds professional touch
4. **Check metadata** - JSON file has detailed info

## Troubleshooting

### Slow generation?
```python
# Disable effects
result = pipeline.generate(keywords, add_effects=False)
```

### Text not visible?
```python
# Use classic template (better contrast)
result = pipeline.generate(keywords, template="classic")
```

### Want more control?
```python
# Use original pipeline
from src.pipeline import Key2PosterPipeline
pipeline = Key2PosterPipeline(...)
```

## Next Steps

1. ✅ Run `python test_unified.py`
2. ✅ Launch `python app_unified.py`
3. ✅ Generate your first poster
4. ✅ Read `UNIFIED_PIPELINE.md` for details
5. ✅ Compare with original pipeline

## Documentation

- `UNIFIED_PIPELINE.md` - Complete documentation
- `ENHANCEMENTS.md` - Enhancement details
- `README.md` - Project overview
