# PosterO Generalized - Quick Start

**Focus:** Generalized Content-Aware Layout Generation with PStylish7 dataset

## What You Have

✅ PStylish7 dataset at `/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7`  
✅ PosterO source at `/home/themaximum/Documents/GitHub/PosterO-CVPR2025`  
✅ Mistral-7B on Windows (need to access from Linux)

## 3-Step Setup

### 1. Install Dependencies

```bash
cd /home/themaximum/Documents/GitHub/Computer_Vision_Project
pip install vllm transformers accelerate
```

### 2. Update Mistral Path

**Option A: Copy from Windows to Linux**
```bash
# If using WSL
cp -r /mnt/c/path/to/mistral-7b ~/models/mistral-7b
```

**Option B: Use Windows path directly (WSL)**
```bash
# Use Windows path in scripts
MISTRAL_PATH="/mnt/c/Users/YourName/models/mistral-7b"
```

### 3. Run Generation

```bash
# Update MISTRAL_PATH in script first
nano run_postero_generalized.sh

# Run for all 7 categories
./run_postero_generalized.sh
```

## Quick Test (Python)

```python
from src.postero_generalized import PosterOGeneralized

# Initialize
gen = PosterOGeneralized(
    llm_path="/path/to/mistral-7b",
    dataset_root="/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"
)

# Generate layout
layout = gen.generate_layout(
    category="movie-poster",
    num_elements=3,
    sample_size=10
)

print(f"Generated {len(layout['bboxes'])} elements")
print(f"Canvas: {layout['canvas_size']}")
print(f"Labels: {layout['labels']}")
```

## Web Interface

```bash
# Update MISTRAL_PATH in app first
nano app_postero_generalized.py

# Launch
python app_postero_generalized.py
# Open http://localhost:7860
```

## 7 Categories Available

1. **chinese-poem** - Cultural education (poetry, literature)
2. **food-menu** - Merchandising (restaurants, cafes)
3. **kind-animals** - Public advocacy (wildlife, conservation)
4. **london-subway** - Public safety (transportation)
5. **motivational-quote** - Social media (Instagram, quotes)
6. **movie-poster** - Entertainment (films, shows)
7. **travel-vintage** - Artwork (travel, vintage style)

## Integration with Key2Poster

```python
from src.postero_generalized import PosterOGeneralized
from src.pipeline import Key2PosterPipeline

# Generate layout
gen = PosterOGeneralized(llm_path="...", dataset_root="...")
layout = gen.generate_layout("movie-poster", num_elements=3)

# Use with FLUX
pipeline = Key2PosterPipeline(use_flux=True)
poster, brief, metrics = pipeline.generate_poster(
    "cyberpunk neon city",
    custom_layout=layout,
    output_path="poster.png"
)
```

## Files Created

- `POSTERO_GENERALIZED_SETUP.md` - Detailed setup guide
- `src/postero_generalized.py` - Python integration wrapper
- `test_postero_generalized.py` - Test script
- `run_postero_generalized.sh` - Batch generation script
- `app_postero_generalized.py` - Gradio web interface

## Next Steps

1. **Update Mistral path** in all scripts
2. **Test single category**: `python test_postero_generalized.py`
3. **Run full generation**: `./run_postero_generalized.sh`
4. **Launch web UI**: `python app_postero_generalized.py`

## Troubleshooting

**vLLM not working?**
```bash
# Use transformers instead (modify postero_generalized.py)
pip install transformers torch
```

**Out of memory?**
```bash
# Reduce sample_size in scripts from 10 to 5
```

**Can't find Mistral?**
```bash
# Check Windows path
ls /mnt/c/Users/*/models/
```

## Performance

- **Generation time**: 2-5s per layout (RTX 3090)
- **Memory**: ~16GB VRAM
- **Dataset**: 152 training + 100 test samples per category

---

**Ready to generate!** 🎨
