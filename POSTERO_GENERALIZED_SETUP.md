# PosterO Generalized Layout Generation Setup

Integration guide for PosterO's Generalized Content-Aware Layout Generation with PStylish7 dataset.

## Quick Setup

### 1. Set Dataset Path

```bash
cd /home/themaximum/Documents/GitHub/PosterO-CVPR2025
# Edit init_path.sh
export DATASET_ROOT="/home/themaximum/Documents/GitHub/Computer_Vision_Project"
source init_path.sh
```

### 2. Install Dependencies

```bash
pip install vllm transformers accelerate
```

### 3. Run Inference (All 7 Categories)

```bash
cd generalized_setting

# Using Mistral-7B (replace with your Windows Mistral path)
source infer.sh 0 /path/to/mistral-7b EXP1
```

This generates layouts for all 7 PStylish7 categories:
- chinese-poem
- food-menu
- kind-animals
- london-subway
- motivational-quote
- movie-poster
- travel-vintage

### 4. Evaluate Results

```bash
source eval.sh /home/themaximum/Documents/GitHub/PosterO-CVPR2025/generalized_setting/mistral-7b/{}/EXP1.pt
```

## Integration with Key2Poster

Use the generated layouts in your poster pipeline:

```python
from src.postero_generalized import PosterOGeneralized

# Initialize
generator = PosterOGeneralized(
    llm_path="/path/to/mistral-7b",
    dataset_root="/home/themaximum/Documents/GitHub/Computer_Vision_Project/PStylish7"
)

# Generate layout for specific category
layout = generator.generate_layout(
    category="movie-poster",
    num_elements=3,
    sample_size=10
)

# Use with FLUX pipeline
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(use_flux=True)
image, brief, metrics = pipeline.generate_poster(
    "cyberpunk neon city",
    custom_layout=layout,
    output_path="poster.png"
)
```

## File Structure

```
Computer_Vision_Project/
├── PStylish7/                    # Dataset (already present)
│   ├── chinese-poem/
│   ├── food-menu/
│   ├── kind-animals/
│   ├── london-subway/
│   ├── motivational-quote/
│   ├── movie-poster/
│   └── travel-vintage/
└── src/
    └── postero_generalized.py    # Integration wrapper

PosterO-CVPR2025/
└── generalized_setting/
    ├── main.py
    ├── infer.sh
    ├── eval.sh
    └── layout_generate/
```

## Categories Mapping

| PStylish7 Category | Purpose | Best For |
|-------------------|---------|----------|
| chinese-poem | Cultural education | Poetry, literature |
| food-menu | Merchandising | Restaurants, cafes |
| kind-animals | Public advocacy | Wildlife, conservation |
| london-subway | Public safety | Transportation, wayfinding |
| motivational-quote | Social media | Instagram, quotes |
| movie-poster | Entertainment | Films, shows |
| travel-vintage | Artwork | Travel, vintage style |

## Performance

| Hardware | Time per Layout | Memory |
|----------|----------------|--------|
| RTX 3090 | ~2-5s | ~16GB |
| RTX 4090 | ~1-3s | ~16GB |

## Troubleshooting

### vLLM Installation Issues

```bash
# Use CPU-only version for testing
pip install vllm-cpu

# Or use transformers directly (slower)
pip install transformers torch
```

### Out of Memory

```bash
# Reduce sample size
python main.py --sample_size 5  # Default is 10
```

### Mistral Path on Windows

If you have Mistral on Windows, mount or copy to Linux:
```bash
# Option 1: Copy from Windows
cp -r /mnt/c/path/to/mistral-7b ~/models/

# Option 2: Use WSL path directly
MODEL_PATH="/mnt/c/Users/YourName/models/mistral-7b"
```

## Summary

```bash
# Complete setup
cd /home/themaximum/Documents/GitHub/PosterO-CVPR2025
echo 'export DATASET_ROOT="/home/themaximum/Documents/GitHub/Computer_Vision_Project"' > init_path.sh
source init_path.sh
pip install vllm transformers accelerate
cd generalized_setting
source infer.sh 0 /path/to/mistral-7b myexp
source eval.sh mistral-7b/{}/myexp.pt
```

Done! 🎨
