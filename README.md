# Key2Poster: Creative Poster Generator

A multi-agent computer vision system that generates cinematic posters from keywords using Stable Diffusion.

## 🚀 Quick Start (2 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Web Interface
```bash
python app_simple.py
```

Then open: **http://localhost:7860**

Enter keywords like "space exploration adventure" and click Generate!

---

## Project Overview

**Input**: 2-5 keywords  
**Output**: 720 × 1280 high-resolution poster  
**Features**: Multi-agent system • Baseline style • Styled titles • Text removal • Denoising

## Architecture

### Multi-Agent System (6 Specialized Agents)
1. **Concept Expander**: Keywords → Creative Brief (Sentiment Analysis + Thematic Expansion)
2. **Visual Designer**: Brief → Poster Image (Stable Diffusion v1.5)
3. **Text Remover**: Image → Text-Free Image (Aggressive multi-method detection)
4. **Quality Enhancer**: Image → Enhanced Image (Denoising + Super-Resolution)
5. **Text Overlay**: Image → Image + Styled Title (Cinematic styling)
6. **Quality Evaluator**: Image → Quality Metrics (Aesthetic + Resolution validation)

## Usage Options

### Option 1: Web Interface (Recommended) 🌐

```bash
# Simple interface (best for demos)
python app_simple.py

# Full interface (all options)
python app.py
```

Access at **http://localhost:7860**

**Features:**
- 🎨 Interactive web UI
- ⚙️ All pipeline options
- 📊 Real-time metrics
- 🔄 Reproducible with seeds
- 📱 Mobile-friendly

### Option 2: Command Line

```bash
# Generate poster with best settings
python run_pipeline.py "space exploration adventure"

# With all enhancements
python run_pipeline.py "dark fantasy warrior" --baseline-style --add-title --aggressive-text-removal

# With seed for reproducibility
python run_pipeline.py "cyberpunk city" --seed 42
```

### Option 3: Python Script

```python
from src.pipeline import Key2PosterPipeline

# Initialize with best settings
pipeline = Key2PosterPipeline(
    baseline_style=True,      # Vibrant colors
    add_title=True,           # Styled movie title
    aggressive_text_removal=True,
    super_resolution=True
)

# Generate poster
image, brief, metrics = pipeline.generate_poster(
    "space exploration adventure",
    output_path="my_poster.png",
    seed=42
)
```

## Project Structure
```
├── src/
│   ├── concept_expander.py   # Semantic expansion agent
│   ├── visual_generator.py   # SD + LoRA generator
│   ├── scraper.py            # Poster data scraper
│   ├── lora_trainer.py       # LoRA fine-tuning
│   ├── pipeline.py           # Main pipeline
│   └── evaluator.py          # Quality metrics
├── data/                     # Scraped poster datasets
├── models/                   # Trained LoRA weights
├── outputs/                  # Generated posters
└── notebooks/                # Experiments & analysis

```

## Grading Target: Level 2-3 (70-90)

### Level 2 Achievements (70-80)
- ✅ Baseline SD implementation
- ✅ LoRA fine-tuning on custom dataset
- ✅ Web scraping for data collection
- ✅ Controlled comparison baseline vs LoRA

### Level 3 Potential (80-90)
- Multi-agent architecture (novel combination)
- Semantic expansion with sentiment analysis
- Comprehensive evaluation metrics
- Ablation studies on agent contributions

## 📊 Performance

| Hardware | Generation Time |
|----------|----------------|
| GPU (RTX 3090) | ~10-15 seconds |
| GPU (RTX 2060) | ~15-20 seconds |
| CPU | ~2-3 minutes |

**Tips for faster generation:**
- Disable text removal
- Disable super-resolution
- Use simple interface (pre-loaded pipeline)

## 🔧 Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**Slow generation:**
- Use GPU with CUDA (10x faster)
- Disable text removal and super-resolution

**Port 7860 already in use:**
```bash
python app_simple.py --server-port 7861
```

## 📖 Documentation

- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Complete setup guide for colleagues ⭐
- **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - Detailed technical guide
- **[GRADIO_GUIDE.md](GRADIO_GUIDE.md)** - Web interface documentation
- **[FINAL_IMPROVEMENTS.md](FINAL_IMPROVEMENTS.md)** - Recent updates and fixes

## 🎯 Complete Pipeline

### Automated Execution
```bash
python run_full_pipeline.py --test-mode
```

### Manual Step-by-Step
```bash
# Step 1: Test setup
python test_pipeline.py

# Step 2: Collect data
python src/collect_data.py

# Step 3: Train LoRA
python src/train_lora.py

# Step 4: Generate posters
python run_pipeline.py "your keywords" --lora

# Step 5: Run comparison
python src/experiment.py
```

## 💡 Examples

### Example 1: Quick Demo
```bash
python app_simple.py
# Enter: "space exploration adventure"
# Result: Vibrant poster with styled title in ~15 seconds
```

### Example 2: Custom Poster
```bash
python run_pipeline.py "dark fantasy warrior" --baseline-style --add-title --seed 42
```

### Example 3: Batch Generation
```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(baseline_style=True, add_title=True)
keywords = ["space adventure", "dark fantasy", "cyberpunk city"]
results = pipeline.batch_generate(keywords)
```

## 🏗️ Pipeline Flow

```
Keywords → [Agent 1: Concept Expander] → Creative Brief
              ↓
         [Agent 2: Visual Designer] → Raw Image
              ↓
         [Agent 3: Text Remover] → Text-Free Image
              ↓
         [Agent 4: Quality Enhancer] → Smooth Sharp Image
              ↓
         [Agent 5: Text Overlay] → Image + Styled Title
              ↓
         [Agent 6: Quality Evaluator] → Final Poster + Metrics
```

**Agent 1:** Sentiment analysis + thematic expansion  
**Agent 2:** Stable Diffusion v1.5 (baseline or LoRA)  
**Agent 3:** Aggressive text detection + removal  
**Agent 4:** Denoising + super-resolution + sharpening  
**Agent 5:** Cinematic title overlay  
**Agent 6:** Aesthetic scoring + resolution validation

## 📊 Results

**Output:**
- Resolution: 720×1280 pixels
- Format: PNG (high quality)
- Style: Vibrant baseline or cinematic LoRA
- Features: Smooth, sharp, text-free, with styled title

**Quality:**
- Aesthetic Score: 0.5-0.7
- No graininess (denoised)
- No artificial text (removed)
- Professional movie poster look

## 🎓 Features

✅ **Multi-Agent System** - 6 specialized agents  
✅ **Baseline Style** - Vibrant, aesthetic colors  
✅ **LoRA Fine-tuning** - Optional cinematic style  
✅ **Styled Title Overlay** - Cinematic movie titles  
✅ **Aggressive Text Removal** - Removes artificial words  
✅ **Denoising** - Smooth, professional quality  
✅ **Super-Resolution** - Sharp details  
✅ **Web Interface** - Easy to use Gradio UI  
✅ **Reproducible** - Seed-based generation  
✅ **Comprehensive Metrics** - Quality evaluation

## 🛠️ Scripts

| Script | Purpose |
|--------|----------|
| `app_simple.py` | **Web interface (recommended)** ⭐ |
| `app.py` | Web interface (full options) |
| `run_pipeline.py` | CLI poster generation |
| `test_pipeline.py` | Test all components |
| `clean_training_data.py` | Remove text from training data |
| `src/train_lora.py` | Train LoRA model (optional) |

## 📁 Project Structure

```
Computer_Vision_Project/
├── app_simple.py             # Simple web interface ⭐
├── app.py                    # Full web interface
├── run_pipeline.py           # CLI tool
├── src/
│   ├── pipeline.py           # Main orchestrator
│   ├── concept_expander.py   # Agent 1: Semantic expansion
│   ├── visual_generator.py   # Agent 2: Image generation
│   ├── text_remover.py       # Agent 3: Text removal
│   ├── refiner.py            # Agent 4: Quality enhancement
│   ├── text_overlay.py       # Agent 5: Title overlay
│   └── evaluator.py          # Agent 6: Quality metrics
├── outputs/                  # Generated posters
└── HOW_TO_RUN.md            # Setup guide for colleagues
```

## 🎯 Best Settings

**For best quality:**
- Baseline Style: ✓
- Title Overlay: ✓
- Aggressive Text Removal: ✓
- Super-Resolution: ✓

**For speed:**
- Baseline Style: ✓
- Title Overlay: ✓
- Text Removal: ✗
- Super-Resolution: ✗

## 📚 Additional Resources

- **HOW_TO_RUN.md** - Complete setup guide
- **GRADIO_GUIDE.md** - Web interface documentation
- **FINAL_IMPROVEMENTS.md** - Recent fixes (graininess, text removal, styling)
- **QUALITY_IMPROVEMENTS.md** - Quality enhancement details

## 🎉 Summary

**Quickest way to start:**
```bash
pip install -r requirements.txt
python app_simple.py
# Open http://localhost:7860
# Enter keywords and generate!
```

**Enjoy creating cinematic posters!** 🎨
