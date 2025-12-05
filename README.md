# Key2Poster: AI-Powered Poster Generation System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FLUX.1](https://img.shields.io/badge/FLUX.1-schnell-green.svg)](https://huggingface.co/black-forest-labs/FLUX.1-schnell)
[![PosterO](https://img.shields.io/badge/PosterO-CVPR%202025-red.svg)](https://github.com/PKU-ICST-MIPL/PosterO_CVPR2025)

Generate professional posters from 2-5 keywords using state-of-the-art AI models with three different layout generation methods.

## 🌟 Features

- **3 Generation Modes**
  - 🎨 Template Mode: Fast generation with editable text layers
  - 🤖 LayoutGAN Mode: Auto-generated adaptive layouts
  - 🔬 PosterO Mode: Content-aware AI layout (CVPR 2025)

- **Advanced Capabilities**
  - ✅ FLUX.1 high-quality image generation
  - ✅ LLM-based prompt enhancement
  - ✅ Interactive text editing (position, size, color)
  - ✅ Multiple poster types (Movie, Event, Product, Music, Sports, etc.)
  - ✅ 7 style presets (Cinematic, Neon, Vintage, Minimalist, etc.)
  - ✅ 720x1280 standardized output

## 📋 Requirements

- **GPU**: CUDA-enabled GPU (FLUX.1 requires ~23GB VRAM)
- **OS**: Linux
- **Python**: 3.10+

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Computer_Vision_Project.git
cd Computer_Vision_Project
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install project dependencies
pip install -r requirements.txt

# Install additional dependencies for FLUX
pip install sentencepiece protobuf

# Install PosterO dependencies (optional)
pip install vllm transformers accelerate
```

### 4. Setup API Keys

Create `.env` file in project root:

```bash
# POE API Key (for PosterO LLM)
POE_API_KEY=your_poe_api_key_here
```

### 5. Download Models

Models will be automatically downloaded on first run:
- FLUX.1-schnell (~23GB)
- Design intent detection model (for PosterO)

## 🎯 Quick Start

### Unified App (Recommended)

Launch the unified interface with all 3 modes:

```bash
python app_unified.py
```

Open browser: `http://localhost:7860`

### Individual Apps

```bash
# Template Mode with editing
python app_editable.py

# PosterO Mode
python app.py

# LayoutGAN Mode
python app_clg_lo.py
```

## 📖 Usage Guide

### 1. Template Mode (Editable)

**Best for**: Quick generation with full editing control

```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(
    use_flux=True,
    use_template=True,
    add_title=True,
    poster_type='movie',
    style_preset='cinematic'
)

image, brief, metrics = pipeline.generate_poster(
    keywords="cyberpunk neon city",
    output_path="outputs/poster.png",
    seed=42
)
```

**Features**:
- ⚡ Fast generation (~10-15s)
- ✏️ Interactive text editing
- 🎨 Position/size/color controls
- 💾 Export with metadata

### 2. LayoutGAN Mode

**Best for**: Adaptive layouts with auto-generation

```python
pipeline = Key2PosterPipeline(
    use_flux=True,
    auto_template=True,
    add_title=True,
    poster_type='event',
    style_preset='bright'
)

image, brief, metrics = pipeline.generate_poster(
    keywords="music festival summer",
    output_path="outputs/poster.png",
    seed=42
)
```

**Features**:
- 🤖 Auto-generated layouts
- 📐 Content-adaptive positioning
- ⚡ Medium speed (~20-30s)

### 3. PosterO Mode (CVPR 2025)

**Best for**: Highest quality with content-aware layouts

```python
from src.pipeline_postero import Key2PosterPosterO

pipeline = Key2PosterPosterO(
    poster_type='movie',
    style_preset='cinematic'
)

image, brief, metrics = pipeline.generate_poster(
    keywords="vintage travel mountains",
    output_path="outputs/poster.png",
    seed=42
)
```

**Features**:
- 🔬 State-of-the-art AI layout
- 🎯 Content-aware positioning
- ⭐ Highest quality (~30-40s)
- 📊 Automatic text/logo/underlay detection

## 🎨 Poster Types

| Type | Description | Best For |
|------|-------------|----------|
| Movie | Cinematic design | Films, entertainment |
| Event | Promotional layout | Concerts, festivals |
| Product | Commercial design | Sales, advertising |
| Music | Concert poster | Bands, albums |
| Sports | Athletic design | Games, competitions |
| Book | Literary design | Books, publications |
| Theater | Stage performance | Plays, shows |
| Conference | Professional layout | Business events |
| Festival | Celebration design | Cultural events |
| Game | Gaming aesthetic | Video games |

## 🎭 Style Presets

| Style | Description | Visual Effect |
|-------|-------------|---------------|
| Cinematic | Dramatic lighting | High contrast, moody |
| Minimalist | Clean composition | Negative space, simple |
| Neon | Vibrant colors | Cyberpunk, glowing |
| Dark | Moody atmosphere | Noir, mysterious |
| Vintage | Retro style | Grain, aged look |
| Bright | High energy | Cheerful, colorful |
| Professional | Corporate polish | Clean, business-like |

## 📁 Project Structure

```
Computer_Vision_Project/
├── src/
│   ├── pipeline.py                    # Main pipeline
│   ├── pipeline_postero.py            # PosterO pipeline
│   ├── pipeline_postero_underlay.py   # PosterO with underlay
│   ├── concept_expander.py            # LLM prompt enhancement
│   ├── visual_generator_flux.py       # FLUX image generation
│   ├── template_generator.py          # Auto template generation
│   ├── evaluator.py                   # Quality evaluation
│   └── ...
├── PosterO/                           # PosterO integration
│   ├── main.py                        # PosterO main script
│   ├── llm_api_wrapper.py            # POE API wrapper
│   ├── design_intent_detect/         # Part 1: Detection
│   └── generalized_setting/          # Part 2: Generation
├── templates/                         # Poster templates
│   ├── template1_layers.json
│   └── ...
├── fonts/                             # Font files
│   └── Graduate-Regular.ttf
├── outputs/                           # Generated posters
├── app_unified.py                     # Unified interface (3 modes)
├── app_editable.py                    # Template editing app
├── app.py                             # PosterO app
├── app_clg_lo.py                      # LayoutGAN app
├── requirements.txt                   # Dependencies
└── README.md                          # This file
```

## 🔧 Advanced Usage

### Batch Generation

```python
keywords_list = [
    "cyberpunk neon city",
    "vintage travel mountains",
    "food restaurant elegant"
]

for i, keywords in enumerate(keywords_list):
    image, brief, metrics = pipeline.generate_poster(
        keywords=keywords,
        output_path=f"outputs/batch_{i}.png",
        seed=42 + i
    )
```

### Custom Text Editing

```python
from add_text_to_poster import add_text_to_poster

add_text_to_poster(
    image_path="outputs/poster.png",
    svg_path="outputs/poster_layout.svg",
    title="CUSTOM TITLE",
    captions=["Subtitle 1", "Subtitle 2"],
    output_path="outputs/poster_edited.png",
    style_prompt="cyberpunk neon"
)
```

### Testing Pipeline

```bash
# Test all 3 modes
python test_pipeline_postero.py

# Test multiple images
python test_multiple_images.py 3

# Test underlay mode
python test_underlay_mode.py
```

## ⚙️ Configuration

### Environment Variables

```bash
# .env file
POE_API_KEY=your_key_here
CUDA_VISIBLE_DEVICES=0
```

### Pipeline Settings

```python
pipeline = Key2PosterPipeline(
    use_flux=True,              # Use FLUX.1 (vs SD)
    use_template=True,          # Use templates
    auto_template=False,        # Auto-generate templates
    add_title=True,             # Add text overlay
    remove_text=False,          # Remove existing text
    super_resolution=False,     # Apply super-resolution
    genre_lora=False,           # Use genre-specific LoRA
    poster_type='movie',        # Poster type
    style_preset='cinematic'    # Style preset
)
```

## 📊 Performance

| Hardware | Template Mode | LayoutGAN Mode | PosterO Mode |
|----------|--------------|----------------|--------------|
| RTX 4090 | ~8-12s | ~15-20s | ~25-30s |
| RTX 3090 | ~10-15s | ~20-25s | ~30-40s |
| RTX 3060 | ~20-30s | ~35-45s | ~50-60s |

## 🐛 Troubleshooting

### CUDA Out of Memory

```bash
# Use sequential CPU offload (already enabled)
# Or reduce batch size / close other GPU apps
```

### "Cannot instantiate tokenizer"

```bash
pip install sentencepiece protobuf
```

### "No module named 'src'"

```bash
# Run from project root
cd Computer_Vision_Project
python app_unified.py
```

### Dimensions not divisible by 8

Fixed automatically - templates now generate FLUX-compatible dimensions.

## 📚 Documentation

- **[Technical Report](TECHNICAL_REPORT.md)** - Architecture and implementation details
- **[PIPELINE_CHANGES.md](PIPELINE_CHANGES.md)** - Pipeline evolution
- **[POSTERO_GENERALIZED_QUICKSTART.md](POSTERO_GENERALIZED_QUICKSTART.md)** - PosterO setup guide

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Additional font support
- [ ] More style presets
- [ ] Multi-language support
- [ ] Real-time preview
- [ ] Cloud deployment

## 📄 License

This project uses:
- FLUX.1-schnell (Apache 2.0)
- PosterO (Research use)
- Custom code (MIT)

## 🙏 Acknowledgments

- **FLUX.1** by Black Forest Labs
- **PosterO** (CVPR 2025) by PKU-ICST-MIPL
- **LayoutGAN** for layout generation
- **POE API** for LLM integration

## 📧 Contact

For questions or issues:
- Open an issue on GitHub
- Email: your.email@example.com

---

**Made with ❤️ using FLUX.1 + PosterO + LayoutGAN**
