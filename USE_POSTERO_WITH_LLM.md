# Using PosterO with LLM (LLaMA 3.1-8B)

## Quick Setup Guide

### Step 1: Download LLaMA 3.1-8B Model

**Option A: Using Hugging Face (Recommended)**
```bash
# Install huggingface-cli
pip install huggingface-hub

# Login to Hugging Face (get token from https://huggingface.co/settings/tokens)
huggingface-cli login

# Download model
huggingface-cli download meta-llama/Meta-Llama-3.1-8B-Instruct --local-dir ./models/llama-3.1-8b
```

**Option B: Manual Download**
1. Go to https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
2. Request access (requires Meta approval)
3. Download model files to `./models/llama-3.1-8b/`

**Option C: Use Alternative Models (No approval needed)**
```bash
# Mistral 7B (similar performance, no approval)
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2 --local-dir ./models/mistral-7b

# Or Qwen 7B
huggingface-cli download Qwen/Qwen2-7B-Instruct --local-dir ./models/qwen-7b
```

### Step 2: Install vLLM

```bash
# Install vLLM for fast inference
pip install vllm

# Verify installation
python -c "import vllm; print('vLLM installed successfully')"
```

### Step 3: Use PosterO with LLM

**Minimal Example:**

```python
from src.layout_gan import PosterO
from PIL import Image

# Initialize with LLM
postero = PosterO(
    llm_path="./models/llama-3.1-8b",  # or mistral-7b, qwen-7b
    canvas_size=(720, 1080),
    device='cuda'
)

# Generate layout
image = Image.new('RGB', (720, 1080), 'white')
layout = postero.generate_layout(image, ["summer", "sale"])
template = postero.layout_to_template(layout)

print(template)
```

**Full Pipeline Example:**

```python
from src.postero_pipeline import PosterOPipeline
from PIL import Image
import json

# Initialize with official PosterO + LLM
pipeline = PosterOPipeline(
    llm_path="./models/llama-3.1-8b",
    canvas_size=(720, 1080),
    use_official=True  # Use official implementation
)

# Generate layout
image = Image.new('RGB', (720, 1080), 'lightblue')
layout = pipeline.generate_layout(
    image, 
    keywords="cyberpunk neon city",
    num_elements=3
)

# Convert to template
template = pipeline.layout_to_template(layout)

# Save template
with open('templates/llm_generated.json', 'w') as f:
    json.dump(template, f, indent=2)

print("Template generated with LLM!")
```

### Step 4: Integrate with Key2Poster

```python
from src.pipeline import Key2PosterPipeline
from src.postero_pipeline import PosterOPipeline

# 1. Generate layout with PosterO + LLM
postero = PosterOPipeline(
    llm_path="./models/llama-3.1-8b",
    use_official=True
)

dummy_img = Image.new('RGB', (720, 1080), 'white')
layout = postero.generate_layout(dummy_img, "anime love story", num_elements=3)
template = postero.layout_to_template(layout)

# Save template
template_path = 'templates/postero_llm.json'
postero.save_template(template, template_path)

# 2. Generate poster with Key2Poster using PosterO layout
pipeline = Key2PosterPipeline(use_flux=True)
image, brief, metrics = pipeline.generate_poster(
    "anime love story japanese",
    template_path=template_path,
    output_path="outputs/postero_llm_poster.png",
    seed=42
)

print(f"Poster generated: {brief['output_path']}")
```

## System Requirements

- **GPU**: NVIDIA GPU with 16GB+ VRAM (for LLaMA 3.1-8B)
- **RAM**: 32GB+ recommended
- **Storage**: ~20GB for model files

## Troubleshooting

**Out of Memory Error:**
```python
# Use smaller model or quantization
postero = PosterO(
    llm_path="./models/mistral-7b",  # Smaller model
    canvas_size=(720, 1080)
)
```

**vLLM Import Error:**
```bash
# Reinstall with CUDA support
pip uninstall vllm
pip install vllm --no-cache-dir
```

**Model Not Found:**
```python
# Check model path
import os
model_path = "./models/llama-3.1-8b"
print(f"Model exists: {os.path.exists(model_path)}")
print(f"Files: {os.listdir(model_path) if os.path.exists(model_path) else 'N/A'}")
```

## Performance Comparison

| Setup | Layout Quality | Speed | VRAM |
|-------|---------------|-------|------|
| Rule-based (no LLM) | ⭐⭐⭐ | Fast (~0.1s) | 0GB |
| LLaMA 3.1-8B | ⭐⭐⭐⭐⭐ | Medium (~2-5s) | 16GB |
| Mistral 7B | ⭐⭐⭐⭐ | Medium (~2-4s) | 14GB |

## Next Steps

1. **Train Design Intent Detector** (optional, improves layout quality):
   ```bash
   cd C:\Users\maxch\Downloads\Homeworks\PosterO-CVPR2025\design_intent_detect
   # Follow README.md for training
   ```

2. **Use Custom Templates**:
   - Generated templates are saved in `templates/`
   - Modify JSON files to customize layouts
   - Use with Key2Poster pipeline

3. **Batch Generation**:
   ```python
   keywords_list = ["summer sale", "winter event", "spring festival"]
   for keywords in keywords_list:
       layout = postero.generate_layout(dummy_img, keywords)
       template = postero.layout_to_template(layout)
       # Use template with Key2Poster...
   ```
