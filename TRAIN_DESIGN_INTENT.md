# Training Design Intent Detector (Optional)

**Note:** This is OPTIONAL. The current system works without it using rule-based detection.
Training improves layout quality by detecting available poster regions more accurately.

## Requirements

- Dataset: PKU PosterLayout or CGL-Dataset
- GPU: 8GB+ VRAM
- Time: ~2-4 hours training

## Quick Setup

### Step 1: Download PKU Dataset from HuggingFace

```bash
# Install dependencies
pip install huggingface-hub datasets

# Download PKU PosterLayout dataset
huggingface-cli download creative-graphic-design/PKU-PosterLayout --repo-type dataset --local-dir C:\Users\maxch\Downloads\Homeworks\poster_dataset\pku
```

Or using Python:
```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="creative-graphic-design/PKU-PosterLayout",
    repo_type="dataset",
    local_dir="C:/Users/maxch/Downloads/Homeworks/poster_dataset/pku"
)
```

### Step 2: Configure Path

Edit `C:\Users\maxch\Downloads\Homeworks\PosterO-CVPR2025\init_path.sh`:
```bash
export DATASET_DIR="C:/Users/maxch/Downloads/Homeworks/poster_dataset"
```

For Windows, create `init_path.bat`:
```batch
set DATASET_DIR=C:\Users\maxch\Downloads\Homeworks\poster_dataset
```

### Step 3: Prepare Data

```bash
cd C:\Users\maxch\Downloads\Homeworks\PosterO-CVPR2025\design_intent_detect
python preprocess.py --dataset pku
```

### Step 4: Train Model

```bash
python main.py --mode train --dataset pku --gpu 0 --epochs 100
```

### Step 5: Test Model

```bash
python main.py --mode test --dataset pku --gpu 0 --weight ./checkpoints/best_model.pth
```

### Step 6: Use Trained Model

```python
from src.layout_gan import PosterO

# Use trained design intent detector
postero = PosterO(
    llm_path="./models/mistral-7b",
    intent_model_path="C:/Users/maxch/Downloads/Homeworks/PosterO-CVPR2025/design_intent_detect/checkpoints/best_model.pth",
    canvas_size=(720, 1080)
)

# Now generates better layouts using trained detector
layout = postero.generate_layout(image, keywords)
```

## Alternative: Skip Training (Use Rule-Based)

**Current system already works without training!**

The rule-based detector provides good results:
```python
from src.postero_pipeline import PosterOPipeline

# Works perfectly without trained model
pipeline = PosterOPipeline(
    llm_path="./models/mistral-7b",
    use_official=False  # Uses rule-based detection
)

layout = pipeline.generate_layout(image, "cyberpunk city", num_elements=3)
```

## Performance Comparison

| Setup | Layout Quality | Training Time | Complexity |
|-------|---------------|---------------|------------|
| Rule-based (current) | ⭐⭐⭐⭐ | 0 (no training) | Easy |
| Trained detector | ⭐⭐⭐⭐⭐ | 2-4 hours | Medium |

## Recommendation

**For most users:** Stick with rule-based detection (no training needed)

**Train only if:**
- You have the PKU/CGL dataset
- You need maximum layout quality
- You're doing research/production deployment

## Summary

```bash
# Current system (NO training needed):
python demo_postero_llm.py  # Already works!

# With training (optional, for advanced users):
cd PosterO-CVPR2025/design_intent_detect
python preprocess.py --dataset pku
python main.py --mode train --dataset pku
```

**Bottom line:** You can skip this step entirely and still get great results! 🚀
