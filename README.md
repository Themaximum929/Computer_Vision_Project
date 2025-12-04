# Key2Poster: AI Poster Generator

Generate professional posters from 2-5 keywords using **FLUX.1** with **template-based composition**.

**Poster Types:** Movie, Advertise, Event, Education, Social, Music, Sports

## Quick Start

```bash
pip install -r requirements.txt
pip install sentencepiece protobuf  # Required for FLUX
python app.py  # HuggingFace Space version
# OR
python app_template.py  # Template editor version
```
Open: **http://localhost:7860**

⚠️ **GPU Required**: FLUX.1 requires CUDA-enabled GPU

---

## Features

✅ **Template-Based Composition** - Random template selection with professional layouts  
✅ **FLUX.1 Image Generation** - High-quality image generation with CUDA acceleration  
✅ **Smart Prompt Enhancement** - Sentiment analysis + thematic expansion (extensible)  
✅ **Multiple Poster Types** - Movie, Advertise, Event, Education, Social, Music, Sports  
✅ **7 Style Presets** - Cinematic, Minimalist, Neon, Dark, Vintage, Bright, Professional  
✅ **Interactive Canvas Editor** - Drag, resize, and edit poster elements  
✅ **LLM Text Processing** - Intelligent title generation from keywords  
✅ **Aesthetic Scoring** - Automated quality evaluation  
✅ **PosterO Generalized Layouts** - LLM-based content-aware layout generation (NEW)  

---

## Applications

### Web Interface (Recommended)
```bash
python app.py                      # HuggingFace Space (GPU required)
python app_template.py             # Template editor with canvas
python app_postero_generalized.py  # PosterO Generalized layouts (NEW)
python app_flux.py                 # Original FLUX interface
```

### Python API
```python
from src.pipeline import Key2PosterPipeline

# Template-based generation (NEW)
pipeline = Key2PosterPipeline(
    use_flux=True,
    add_title=False,  # Text added via template
    genre_lora=False,
    remove_text=True,
    aggressive_text_removal=True
)

image, brief, metrics = pipeline.generate_poster(
    "summer sale event",
    output_path="poster.png",
    seed=42
)

# Template info available in brief['template']
print(f"Template size: {brief['template']['size']}")
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

## New Pipeline (5 Steps)

### 1. **Template Selection**
- Randomly selects poster template from `templates/` folder
- Extracts image region dimensions and text placement
- Supports multiple layout variations

### 2. **Prompt Enhancement** 🔧 TODO
- Current: Basic sentiment analysis + thematic expansion
- **Extensible**: Teammates can enhance `src/concept_expander.py`
- Receives template image size for context-aware enhancement
- Returns enhanced prompt optimized for FLUX generation

### 3. **FLUX Image Generation**
- Generates high-quality image using FLUX.1-schnell
- Automatically resizes to fit template's image region
- Clean image without text (text added separately)

### 4. **Template Composition**
- Merges FLUX image with template background
- Places image in designated region from template
- Adds LLM-processed text overlay with proper positioning

### 5. **Quality Evaluation**
- Aesthetic scoring
- Resolution validation
- Saves final composed poster

---

## Template System

### Template Structure
Templates are JSON files in `templates/` folder:
```json
{
  "size": [720, 1080],
  "layers": [
    {
      "name": "Background",
      "bbox": [0, 0, 720, 1080]
    },
    {
      "name": "Image",
      "bbox": [54, 59, 655, 873]
    },
    {
      "name": "Text",
      "bbox": [240, 930, 472, 989]
    }
  ]
}
```

### Adding New Templates
1. Create `templates/templateN_layers.json`
2. Define poster size and layer bounding boxes
3. Pipeline automatically detects and uses new templates

---

## Project Structure

```
├── src/
│   ├── pipeline.py                  # Main orchestrator (5-step pipeline)
│   ├── concept_expander.py          # Prompt enhancement (TODO: extend here)
│   ├── visual_generator_flux.py     # FLUX.1 image generation
│   ├── evaluator.py                 # Quality evaluation
│   └── ...
├── templates/
│   ├── template1_layers.json        # Poster layout templates
│   ├── template2_layers.json
│   └── ...
├── fonts/
│   └── Graduate-Regular.ttf         # Text overlay font
├── app.py                           # HuggingFace Space (GPU)
├── app_template.py                  # Template editor with canvas
├── app_flux.py                      # Original FLUX interface
└── requirements.txt                 # Dependencies
```

---

## Performance

| Hardware | Time per Poster |
|----------|----------------|
| RTX 3090 | ~10-15s |
| RTX 4090 | ~8-12s |
| RTX 3060 | ~20-30s |
| CPU | ❌ Not supported (GPU required) |

---

## Examples

```bash
# Template-based generation
python app_template.py
# Input: "anime love story japanese"
# Output: Random template + FLUX image + title overlay

# HuggingFace Space
python app.py
# Input: "cyberpunk neon city"
# Type: Movie, Style: Neon
# Output: Professional poster with template composition
```

### Canvas Editor Features
- 🖱️ Drag elements to reposition
- 🔄 Resize with corner handles
- 🖊️ Double-click text to edit
- 💾 Export final poster as PNG

---

## Documentation

- **PIPELINE_CHANGES.md** - New 5-step pipeline details
- **POSTERO_GENERALIZED_QUICKSTART.md** - PosterO Generalized setup (NEW)
- **POSTERO_GENERALIZED_SETUP.md** - Detailed PosterO integration guide
- **requirements.txt** - Dependencies (includes sentencepiece)
- **templates/** - Poster layout templates

## For Teammates: Extending Prompt Enhancement

To enhance the prompt generation (Step 2), modify `src/concept_expander.py`:

```python
def expand(self, keywords, image_size=None):
    # Current: Basic sentiment + themes
    # TODO: Add your advanced enhancement here
    # - Use image_size for context
    # - Add more sophisticated NLP
    # - Integrate external APIs
    # - Optimize for FLUX generation
    
    return {
        'prompt': enhanced_prompt,
        'sentiment': sentiment,
        'confidence': confidence,
        'mood': mood,
        'themes': themes
    }
```

The pipeline will automatically use your enhanced prompts!

---

## Models

- **FLUX.1-schnell** - Fast image generation (4 steps, ~23GB VRAM)
- **Graduate-Regular.ttf** - Text overlay font
- **Templates** - JSON-based layout definitions

---

## Troubleshooting

### "CUDA not available" Error
```bash
# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### "Cannot instantiate tokenizer" Error
```bash
# Install missing dependencies
pip install sentencepiece protobuf
```

### "No module named 'src'" Error
```bash
# Run from project root, not from src/ folder
cd Computer_Vision_Project
python app.py
```

---

## Summary

```bash
# Quick Start
pip install -r requirements.txt
pip install sentencepiece protobuf
python app_template.py  # Template editor
# OR
python app.py  # HuggingFace Space
```

**Result:** Professional template-based posters with FLUX.1 generation! 🎨

---

## Key Improvements

✅ **Template-based composition** - Consistent professional layouts  
✅ **Random template selection** - Variety in every generation  
✅ **Extensible prompt enhancement** - Easy for teammates to improve  
✅ **Interactive canvas editor** - Full control over final design  
✅ **GPU-optimized** - Fast generation with CUDA acceleration  
✅ **HuggingFace Space ready** - Deploy with @spaces.GPU decorator  
✅ **PosterO Generalized** - LLM-based content-aware layout generation (NEW)

---

## PosterO Generalized Layout Generation (NEW)

Generate content-aware layouts using LLM-based in-context learning with PStylish7 dataset.

### Quick Start

```bash
# Install dependencies
pip install vllm transformers accelerate

# Run generation
./run_postero_generalized.sh

# Or use Python API
python test_postero_generalized.py
```

### 7 Categories Available

1. **chinese-poem** - Cultural education
2. **food-menu** - Merchandising display
3. **kind-animals** - Public advocacy
4. **london-subway** - Public safety
5. **motivational-quote** - Social media
6. **movie-poster** - Entertainment marketing
7. **travel-vintage** - Artwork exhibition

### Python API

```python
from src.postero_generalized import PosterOGeneralized

gen = PosterOGeneralized(
    llm_path="/path/to/mistral-7b",
    dataset_root="./PStylish7"
)

layout = gen.generate_layout(
    category="movie-poster",
    num_elements=3,
    sample_size=10
)

print(f"Generated {len(layout['bboxes'])} elements")
```

**See:** `POSTERO_GENERALIZED_QUICKSTART.md` for detailed setup
