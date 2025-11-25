# Key2Poster: AI Poster Generator

Generate professional posters from 2-5 keywords using FLUX.1 or Stable Diffusion with LoRA fine-tuning.

**Poster Types:** Movie, Advertise, Event, Education, Social, Music, Sports

## Quick Start

```bash
pip install -r requirements.txt
python app_flux.py
```
Open: **http://localhost:7860**

---

## Features

✅ **FLUX.1 Text Generation** - Native text rendering (no PIL overlay)  
✅ **Multiple Poster Types** - Movie, Advertise, Event, Education, Social, Music, Sports  
✅ **7 Style Presets** - Cinematic, Minimalist, Neon, Dark, Vintage, Bright, Professional  
✅ **Genre Detection** - Auto-classify content genre  
✅ **Text Removal** - Aggressive multi-method detection  
✅ **Quality Enhancement** - Denoising + super-resolution  
✅ **Aesthetic Scoring** - Automated quality evaluation  

---

## Applications

### Web Interface (Recommended)
```bash
python app_flux.py        # FLUX with poster types
python app_simple.py      # SD 1.5 baseline
python app_unified.py     # SD 1.5 with LoRA
```

### Command Line
```bash
python run_pipeline_flux.py "cyberpunk city" --style neon --type advertise
```

### Python API
```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=True,
    poster_type='advertise',
    style_preset='bright'
)

image, brief, metrics = pipeline.generate_poster(
    "summer sale event",
    output_path="poster.png",
    seed=42
)
```

---

## Poster Types

| Type | Description | Best For |
|------|-------------|----------|
| Movie | Cinematic poster design | Films, entertainment |
| Advertise | Commercial design | Products, sales |
| Event | Promotional design | Concerts, festivals |
| Education | Informative layout | Schools, training |
| Social | Awareness campaigns | Causes, movements |
| Music | Concert poster | Bands, festivals |
| Sports | Athletic design | Games, competitions |

---

## Style Presets

| Style | Description |
|-------|-------------|
| Cinematic | Dramatic lighting, high contrast |
| Minimalist | Clean composition, negative space |
| Neon | Vibrant neon colors, cyberpunk |
| Dark | Moody atmosphere, noir style |
| Vintage | Retro style, grain texture |
| Bright | High energy, cheerful |
| Professional | Corporate, polished |

---

## Multi-Agent System (7 Agents)

1. **Concept Expander** - Sentiment analysis + thematic expansion
2. **Genre Classifier** - Auto-detect genre from keywords
3. **Visual Designer** - FLUX.1 or SD 1.5 + genre-specific LoRA
4. **Text Remover** - Aggressive multi-method text detection
5. **Quality Enhancer** - Denoising + super-resolution
6. **Text Overlay** - FLUX native text generation
7. **Quality Evaluator** - Aesthetic scoring + validation

---

## Training Workflow

### 1. Collect Data
```bash
python src/collect_data.py
```
Scrapes movie posters from IMDB → `data/posters/`

### 2. Preprocess
```bash
python preprocess_training_data.py
```
Removes text from posters → `data/posters_clean/`

### 3. Train LoRA
```bash
python src/train_lora.py --data-dir data/posters_clean
```
Trains genre-specific LoRA models → `models/`

---

## Project Structure

```
├── src/
│   ├── pipeline.py                  # Main orchestrator
│   ├── concept_expander.py          # Agent 1
│   ├── genre_classifier.py          # Agent 2
│   ├── visual_generator.py          # Agent 3 (SD 1.5)
│   ├── visual_generator_flux.py     # Agent 3 (FLUX)
│   ├── text_remover.py              # Agent 4
│   ├── aggressive_text_remover.py   # Agent 4 (advanced)
│   ├── refiner.py                   # Agent 5
│   ├── super_resolution.py          # Agent 5
│   ├── enhanced_flux_text.py        # Agent 6 (FLUX text)
│   ├── evaluator.py                 # Agent 7
│   ├── lora_trainer.py              # LoRA training
│   └── train_lora.py                # Training script
├── app_flux.py                      # FLUX web UI
├── app_simple.py                    # SD 1.5 web UI
├── app_unified.py                   # SD 1.5 + LoRA web UI
├── run_pipeline_flux.py             # CLI tool
└── preprocess_training_data.py      # Preprocessing
```

---

## Performance

| Hardware | Time per Image |
|----------|----------------|
| RTX 3090 | ~10-15s |
| RTX 2060 | ~15-20s |
| CPU | ~2-3min |

---

## Examples

```bash
# Movie poster
python app_flux.py
# Input: "space exploration adventure"
# Type: Movie, Style: Cinematic

# Event poster
# Input: "summer music festival"
# Type: Event, Style: Bright

# Social awareness
# Input: "save the ocean"
# Type: Social, Style: Minimalist

# Advertisement
# Input: "fresh organic food"
# Type: Advertise, Style: Professional
```

---

## Documentation

- **FLUX_ENHANCEMENTS.md** - FLUX text generation details
- **PROJECT_STRUCTURE.md** - Clean project structure
- **requirements.txt** - Dependencies

---

## Models

- **FLUX.1-schnell** - Fast text generation (4 steps, ~23GB)
- **Stable Diffusion 1.5** - Baseline model
- **Genre-specific LoRA** - Action, Horror, Sci-Fi, Romance, Comedy, Fantasy

---

## Testing

```bash
# Test FLUX
python test_flux.py

# Test FLUX text generation
python test_flux_text_generation.py

# Test enhancements
python test_flux_enhanced.py

# Full comparison
python test_flux_text_generation_enhanced.py
```

---

## Summary

```bash
# Complete workflow
python src/collect_data.py                           # Collect data
python preprocess_training_data.py                   # Preprocess
python src/train_lora.py --data-dir data/posters_clean  # Train
python app_flux.py                                   # Generate

# Quick generation
python app_flux.py  # Web UI
```

**Result:** Professional posters with FLUX text generation! 🎨
