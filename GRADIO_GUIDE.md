# Gradio Web Interface Guide

## Quick Start

### Install Gradio
```bash
pip install gradio>=4.0.0
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### Launch Interface

#### Option 1: Full Interface (All Options)
```bash
python app.py
```
- All pipeline options available
- Presets for quick configuration
- Detailed metrics display
- Best for: Experimentation and demos

#### Option 2: Simple Interface (Quick Demo)
```bash
python app_simple.py
```
- Pre-configured with best settings
- Minimal options (just keywords + seed)
- Faster startup
- Best for: Quick demos and presentations

### Access Interface
Open browser and go to:
```
http://localhost:7860
```

Or use the URL shown in terminal.

---

## Full Interface (app.py)

### Features

**Input Section:**
- Keywords input (2-5 words)
- Generation settings (LoRA, No-Text Mode)
- Enhancement settings (Text Removal, Super-Resolution)
- Seed for reproducibility

**Output Section:**
- Generated poster image (720×1280)
- Detailed generation info
- Quality metrics
- Generation time

**Quick Presets:**
- ⭐ **Best Quality** - All enhancements enabled
- ⚡ **Fast** - Minimal processing for speed
- 🧪 **Experimental** - Aggressive settings

**Examples:**
- Pre-configured example keywords
- Click to try instantly

### Settings Explained

#### Generation Settings

**Use LoRA Fine-tuning** ✓ (Recommended)
- Uses fine-tuned model for movie poster style
- Better composition and aesthetics
- Trained on 50+ movie posters

**No-Text Mode** ✓ (Recommended)
- Generates at optimal resolution (576×1024)
- Prevents text artifacts
- 95%+ text-free success rate

#### Enhancement Settings

**Enable Text Removal** ✓
- Detects and removes artificial text
- Standard: 1 pass, basic detection
- Recommended for clean posters

**Aggressive Text Removal**
- 3 passes with multi-method detection
- Slower but more thorough
- Use if standard removal misses text

**Super-Resolution Enhancement** ✓ (Recommended)
- Advanced sharpening
- Detail enhancement
- Fixes blur issues

#### Advanced

**Seed**
- 0 = Random generation
- Any number > 0 = Reproducible results
- Use same seed to regenerate exact poster

### Presets

#### ⭐ Best Quality
```
LoRA: ✓
No-Text Mode: ✓
Text Removal: ✓
Aggressive: ✗
Super-Resolution: ✓
```
**Use for:** Final posters, presentations

#### ⚡ Fast
```
LoRA: ✓
No-Text Mode: ✓
Text Removal: ✗
Aggressive: ✗
Super-Resolution: ✗
```
**Use for:** Quick tests, iterations

#### 🧪 Experimental
```
LoRA: ✓
No-Text Mode: ✗
Text Removal: ✓
Aggressive: ✓
Super-Resolution: ✓
```
**Use for:** Maximum text removal

---

## Simple Interface (app_simple.py)

### Features

**Pre-configured with best settings:**
- LoRA fine-tuning enabled
- No-Text Mode enabled
- Super-Resolution enabled
- Text removal enabled

**Inputs:**
- Keywords (2-5 words)
- Seed (optional)

**Outputs:**
- Generated poster
- Basic info (sentiment, aesthetic score, time)

**Advantages:**
- Faster startup (pipeline loaded once)
- Simpler UI
- Best settings by default
- Perfect for demos

---

## Usage Examples

### Example 1: Generate Poster
1. Enter keywords: `space exploration adventure`
2. Click "Generate Poster"
3. Wait ~15-20 seconds
4. View result and metrics

### Example 2: Reproducible Generation
1. Enter keywords: `dark fantasy warrior`
2. Set seed: `42`
3. Generate
4. Use same seed later to get exact same poster

### Example 3: Compare Settings
1. Generate with "Best Quality" preset
2. Note the seed used
3. Generate again with "Fast" preset (same seed)
4. Compare results

### Example 4: Batch Generation
1. Use examples section
2. Click each example
3. Compare different styles

---

## API Usage (Programmatic)

### Using the Gradio Interface Programmatically

```python
import gradio as gr
from app import generate_poster

# Generate poster
image, info = generate_poster(
    keywords="space adventure",
    use_lora=True,
    no_text_mode=True,
    remove_text=True,
    aggressive_text_removal=False,
    super_resolution=True,
    seed=42
)

# Save image
image.save("my_poster.png")
print(info)
```

### Direct Pipeline Usage

```python
from src.pipeline import Key2PosterPipeline

# Initialize
pipeline = Key2PosterPipeline(
    use_lora=True,
    no_text_mode=True,
    super_resolution=True
)

# Generate
image, brief, metrics = pipeline.generate_poster(
    "space adventure",
    output_path="poster.png",
    seed=42
)
```

---

## Deployment

### Local Network Access
```bash
# Allow access from other devices on network
python app.py
# Access from other devices: http://YOUR_IP:7860
```

### Public Sharing (Gradio Share)
```python
# In app.py, change:
demo.launch(share=True)  # Creates public URL
```

### Production Deployment

#### Using Hugging Face Spaces
1. Create account on huggingface.co
2. Create new Space (Gradio)
3. Upload `app.py` and `src/` folder
4. Add `requirements.txt`
5. Space will auto-deploy

#### Using Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

---

## Troubleshooting

### Interface won't start
```bash
# Check Gradio installation
pip install --upgrade gradio

# Check port availability
# Try different port in app.py:
demo.launch(server_port=7861)
```

### Pipeline loading slow
```bash
# Use simple interface (pre-loads pipeline)
python app_simple.py
```

### Out of memory
```bash
# Reduce batch size or use CPU
# In visual_generator.py, set device="cpu"
```

### Can't access from other devices
```bash
# Make sure firewall allows port 7860
# Use server_name="0.0.0.0" in launch()
```

---

## Performance Tips

### Faster Generation
1. Use "Fast" preset
2. Disable text removal
3. Disable super-resolution
4. Use simple interface

### Better Quality
1. Use "Best Quality" preset
2. Enable all enhancements
3. Use LoRA fine-tuning
4. Use No-Text Mode

### Caching
- Full interface caches pipelines per configuration
- Simple interface loads pipeline once
- Subsequent generations are faster

---

## Customization

### Change Theme
```python
# In app.py
demo = gr.Blocks(theme=gr.themes.Glass())  # or Soft(), Monochrome()
```

### Add More Examples
```python
gr.Examples(
    examples=[
        ["your keywords", True, True, True, False, True, 42],
        # Add more...
    ],
    inputs=[...],
)
```

### Modify Layout
```python
with gr.Row():
    with gr.Column(scale=1):
        # Left side
    with gr.Column(scale=2):
        # Right side (larger)
```

---

## Integration with Other Tools

### Jupyter Notebook
```python
import gradio as gr
from app import generate_poster

# Launch in notebook
demo.launch(inline=True)
```

### REST API
```python
# Gradio automatically creates API
# Access at: http://localhost:7860/api/
# Documentation: http://localhost:7860/docs
```

### Python Script
```python
from gradio_client import Client

client = Client("http://localhost:7860")
result = client.predict(
    "space adventure",  # keywords
    True,  # use_lora
    True,  # no_text_mode
    # ... other params
    api_name="/predict"
)
```

---

## Summary

### Quick Commands
```bash
# Full interface
python app.py

# Simple interface
python app_simple.py

# Install Gradio
pip install gradio>=4.0.0
```

### Best Practices
- ✅ Use "Best Quality" preset for final posters
- ✅ Use "Fast" preset for testing
- ✅ Set seed for reproducible results
- ✅ Use simple interface for demos
- ✅ Use full interface for experimentation

### Features
- 🎨 Interactive web interface
- ⚙️ All pipeline options available
- 📊 Real-time metrics display
- 🔄 Reproducible with seeds
- 🚀 Quick presets
- 📱 Mobile-friendly
- 🌐 Shareable (with share=True)

**Access the interface at http://localhost:7860 after launching!**
