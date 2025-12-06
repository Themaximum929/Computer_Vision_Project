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

## 🔄 System Architecture Flow

```
User Keywords → LLM (POE API) → Enhanced Prompt → FLUX.1 → Base Image
                                                              ↓
                                                    Layout Generation
                                                    ┌─────────┬─────────┬─────────┐
                                                    │Template │LayoutGAN│ PosterO │
                                                    │  Mode   │  Mode   │  Mode   │
                                                    └─────────┴─────────┴─────────┘
                                                              ↓
                                                    Text Rendering → Final Poster
```

### Key Components:
1. **LLM Integration**: POE API (Claude Sonnet 4.5) for prompt enhancement
2. **Image Generation**: FLUX.1-schnell (4-step inference)
3. **Layout Engine**: Template/LayoutGAN/PosterO (3 modes)
4. **Text Rendering**: Dynamic font sizing + contrast-based coloring

## 🚀 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/Computer_Vision_Project.git
cd Computer_Vision_Project
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows
```

### Step 3: Install Core Dependencies

```bash
# Install PyTorch with CUDA support (REQUIRED)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install project dependencies
pip install -r requirements.txt

# Install FLUX dependencies
pip install sentencepiece protobuf
```

### Step 4: Setup LLM API (POE)

**Why POE?** We use POE API instead of downloading LLaMA 3.1-8B (16GB) to save disk space and enable cloud-based LLM inference.

1. **Get POE API Key**:
   - Visit [poe.com](https://poe.com)
   - Sign up/login
   - Go to Settings → API Keys
   - Create new API key

2. **Create `.env` file** in project root:

```bash
# POE API Key (for LLM prompt enhancement)
POE_API_KEY=your_poe_api_key_here

# Optional: Specify GPU
CUDA_VISIBLE_DEVICES=0
```

**LLM Flow**: `Keywords → POE API (Claude Sonnet 4.5) → Enhanced Description + Title + Captions`

### Step 5: Install PosterO (Optional - for PosterO Mode)

**PosterO** provides state-of-the-art content-aware layout generation (CVPR 2025).

```bash
# Clone PosterO repository
git clone https://github.com/PKU-ICST-MIPL/PosterO_CVPR2025 PosterO
cd PosterO

# Install PosterO dependencies
pip install vllm transformers accelerate timm opencv-python pandas segmentation-models-pytorch CairoSVG

# Download design intent detection model weights
# Visit: https://drive.google.com/drive/folders/1CUv13fZvySk1AV-r-7jbBX0wRCyVFFQG
# Download and place in: PosterO/design_intent_detect/pku_128_1e-06_none/ckpt/

cd ..
```

**PosterO Flow**:
```
FLUX Image → Part 1: Design Intent Detection (CNN) → Available Areas
                                                           ↓
                                      Part 2: LLM Layout Generation (POE API)
                                                           ↓
                                                    SVG Layout (bbox)
                                                           ↓
                                                  Text Rendering → Final Poster
```

### Step 6: Install RALF (Optional - for Advanced Layout)

**RALF** provides retrieval-augmented layout generation (CVPR 2024).

```bash
# Clone RALF repository
git clone https://github.com/CyberAgentAILab/RALF
cd RALF

# Install RALF dependencies (using Poetry)
curl -sSL https://install.python-poetry.org | python3 -
poetry install

# Download pre-trained weights (optional)
# Visit: https://drive.google.com/file/d/1b357gVAnCSqMfbP3Cc2ey6LCeoohfYAi/view

cd ..
```

**RALF Flow**: `Content Image → Retrieve Similar Layouts → Adapt Layout → Generate`

### Step 7: Download Models (Automatic)

Models will be automatically downloaded on first run:
- **FLUX.1-schnell** (~23GB) - from Hugging Face
- **Design intent model** (for PosterO) - manual download required

### Step 8: Verify Installation

```bash
# Test basic pipeline
python -c "from src.pipeline import Key2PosterPipeline; print('✓ Installation successful!')"

# Test FLUX availability
python -c "import torch; print(f'✓ CUDA available: {torch.cuda.is_available()}')"

# Test POE API
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'✓ POE API Key: {os.getenv(\"POE_API_KEY\")[:10]}...')"
```

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
├── src/                               # Core pipeline modules
│   ├── pipeline.py                    # Main pipeline (Template/LayoutGAN)
│   ├── pipeline_postero.py            # PosterO pipeline
│   ├── pipeline_postero_underlay.py   # PosterO with underlay
│   ├── concept_expander.py            # LLM prompt enhancement (POE API)
│   ├── visual_generator_flux.py       # FLUX.1 image generation
│   ├── template_generator.py          # Auto template generation
│   ├── evaluator.py                   # Quality evaluation
│   └── Dataset/                       # Training datasets (gitignored)
├── PosterO/                           # PosterO integration (install separately)
│   ├── main.py                        # PosterO main script
│   ├── llm_api_wrapper.py            # POE API wrapper (replaces LLaMA)
│   ├── design_intent_detect/         # Part 1: CNN-based detection
│   │   └── ckpt/                     # Model weights (download required)
│   └── generalized_setting/          # Part 2: LLM generation
├── RALF/                              # RALF integration (install separately)
│   ├── image2layout/                 # Layout generation modules
│   └── configs/                      # Configuration files
├── templates/                         # Poster templates (JSON)
│   ├── template1_layers.json
│   ├── template2_layers.json
│   └── ...
├── fonts/                             # Font files
│   └── Graduate-Regular.ttf
├── outputs/                           # Generated posters
├── app_unified.py                     # Unified interface (3 modes)
├── app_editable.py                    # Template editing app
├── app.py                             # PosterO app
├── app_clg_lo.py                      # LayoutGAN app
├── add_text_to_poster.py             # Text rendering module
├── combine_simple.py                 # PosterO Part 1 + Part 2 integration
├── test_pipeline_postero.py          # Testing script
├── requirements.txt                   # Dependencies
├── .env                               # API keys (create manually)
├── .gitignore                         # Git ignore rules
├── LICENSE                            # MIT + Third-party licenses
└── README.md                          # This file
```

## 🔍 Detailed Pipeline Flow

### Template Mode Flow
```
1. User Input: "cyberpunk neon city"
   ↓
2. Concept Expander (POE API):
   - Input: keywords + poster_type + style_preset
   - Output: enhanced_description, title, 3 captions
   ↓
3. Template Selection:
   - Load JSON template (6 types: split, grid, hero, sidebar, asymmetric, minimal)
   - Extract image region bbox
   ↓
4. FLUX.1 Generation:
   - Input: enhanced_description, dimensions (÷8 validated)
   - Output: base image (512x768 or template size)
   ↓
5. Template Composition:
   - Place FLUX image in template region
   - Add background colors/gradients
   ↓
6. Text Rendering:
   - Dynamic font sizing (60% of bbox height max)
   - Contrast-based color selection
   - Smooth anti-aliasing with circular outline
   ↓
7. Post-Processing:
   - Resize to 720x1280
   - Quality evaluation
   - Save with metadata
```

### PosterO Mode Flow
```
1. User Input: "vintage travel mountains"
   ↓
2. Concept Expander (POE API):
   - Same as Template Mode
   ↓
3. FLUX.1 Generation:
   - Generate 512x768 base image
   - Resize to 513x750 (PosterO input size)
   ↓
4. PosterO Part 1 - Design Intent Detection:
   - CNN model detects available areas
   - Input: 513x750 image
   - Output: heatmap → grid-based regions (3x2 cells)
   ↓
5. PosterO Part 2 - LLM Layout Generation:
   - POE API generates SVG layout
   - Input: available_areas + element_types
   - Output: SVG with bounding boxes (text, logo, underlay)
   ↓
6. Text Rendering:
   - Parse SVG for text element bboxes
   - Upscale to 720x1280 (scale bboxes proportionally)
   - Render title + captions with dynamic sizing
   ↓
7. Post-Processing:
   - Quality evaluation
   - Save poster + SVG layout
```

### LayoutGAN Mode Flow
```
1. User Input: "music festival summer"
   ↓
2. Concept Expander (POE API):
   - Same as Template Mode
   ↓
3. Auto Template Generation:
   - LayoutGAN generates adaptive layout
   - Content-aware positioning
   ↓
4. FLUX.1 Generation:
   - Generate image for layout region
   ↓
5. Text Rendering + Post-Processing:
   - Same as Template Mode
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

## 🔗 External Dependencies

### Required
- **FLUX.1-schnell**: Auto-downloaded from Hugging Face (~23GB)
- **POE API**: Cloud-based LLM (requires API key)

### Optional (for PosterO Mode)
- **PosterO**: [GitHub](https://github.com/PKU-ICST-MIPL/PosterO_CVPR2025)
- **Design Intent Model**: [Google Drive](https://drive.google.com/drive/folders/1CUv13fZvySk1AV-r-7jbBX0wRCyVFFQG)

### Optional (for Advanced Features)
- **RALF**: [GitHub](https://github.com/CyberAgentAILab/RALF)
- **PKU PosterLayout Dataset**: [GitHub](https://github.com/PKU-ICST-MIPL/PosterLayout-CVPR2023)
- **CGL Dataset**: [GitHub](https://github.com/minzhouGithub/CGL-GAN)

## 📚 Documentation

- **[Technical Report](TECHNICAL_REPORT.md)** - Architecture and implementation details
- **[PIPELINE_CHANGES.md](PIPELINE_CHANGES.md)** - Pipeline evolution
- **[POSTERO_GENERALIZED_QUICKSTART.md](POSTERO_GENERALIZED_QUICKSTART.md)** - PosterO setup guide

## 🔑 API Keys and Credentials

### POE API Setup (Required for LLM)

1. **Why POE instead of local LLaMA?**
   - Saves 16GB disk space (no model download)
   - Cloud-based inference (no local GPU for LLM)
   - Access to Claude Sonnet 4.5 (better quality)

2. **Get API Key**:
   ```
   1. Visit https://poe.com
   2. Sign up/login
   3. Settings → API Keys
   4. Create new key
   5. Copy to .env file
   ```

3. **Usage in Code**:
   ```python
   # PosterO/llm_api_wrapper.py
   from poe_api_wrapper import PoeApi
   
   client = PoeApi(os.getenv("POE_API_KEY"))
   response = client.send_message("Claude-Sonnet-4.5", prompt)
   ```

### Hugging Face Token (Optional)

For faster FLUX.1 downloads:
```bash
huggingface-cli login
# Enter your token from https://huggingface.co/settings/tokens
```

## 🎓 Learning Resources

### Papers
- **FLUX.1**: [Black Forest Labs Blog](https://blackforestlabs.ai/announcing-black-forest-labs/)
- **PosterO**: [CVPR 2025 Paper](https://openaccess.thecvf.com/content/CVPR2025/html/Hsu_PosterO_Structuring_Layout_Trees_to_Enable_Language_Models_in_Generalized_CVPR_2025_paper.html)
- **RALF**: [CVPR 2024 Paper](https://arxiv.org/abs/2311.13602)

### Tutorials
- **FLUX.1 Guide**: [Hugging Face Docs](https://huggingface.co/docs/diffusers/api/pipelines/flux)
- **POE API**: [Documentation](https://creator.poe.com/docs/quick-start)
- **Gradio**: [Official Guide](https://www.gradio.app/guides/quickstart)

## 📚 Documentation

- **[Technical Report](TECHNICAL_REPORT.md)** - Architecture and implementation details
- **[PIPELINE_CHANGES.md](PIPELINE_CHANGES.md)** - Pipeline evolution
- **[POSTERO_GENERALIZED_QUICKSTART.md](POSTERO_GENERALIZED_QUICKSTART.md)** - PosterO setup guide

## 🎯 Quick Start Examples

### Example 1: Generate Movie Poster
```bash
python app_unified.py
# In browser:
# - Mode: Template
# - Keywords: "space adventure astronaut"
# - Type: Movie
# - Style: Cinematic
# - Click Generate
```

### Example 2: Generate Event Poster with PosterO
```bash
python app.py
# In browser:
# - Keywords: "summer music festival beach"
# - Type: Event
# - Style: Bright
# - Click Generate
```

### Example 3: Batch Generation
```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(use_flux=True, use_template=True)

keywords = [
    "cyberpunk neon city",
    "vintage travel mountains",
    "food restaurant elegant"
]

for i, kw in enumerate(keywords):
    image, brief, metrics = pipeline.generate_poster(
        keywords=kw,
        output_path=f"outputs/poster_{i}.png",
        seed=42
    )
    print(f"Generated {i+1}/{len(keywords)}: {brief['title']}")
```

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
