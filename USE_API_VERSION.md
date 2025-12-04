# Use HuggingFace API (No Local GPU Needed)

Your GPU has 10.56GB VRAM but Mistral-7B needs ~16GB. Use HuggingFace Inference API instead!

## Setup (1 minute)

### 1. Get HuggingFace Token

Visit: https://huggingface.co/settings/tokens

Click "New token" → Create (read access is enough)

### 2. Set Token

```bash
export HF_TOKEN="hf_your_token_here"
```

### 3. Test

```bash
python3 test_postero_api.py
```

## Python Usage

```python
from src.postero_generalized_api import PosterOGeneralizedAPI

# Initialize with API
generator = PosterOGeneralizedAPI(
    hf_token="hf_your_token_here",
    dataset_root="./PStylish7"
)

# Generate layout (uses HuggingFace API, no local GPU)
layout = generator.generate_layout(
    category="movie-poster",
    num_elements=3,
    sample_size=10
)

print(f"Generated {len(layout['bboxes'])} elements")
```

## Benefits

✅ **No GPU needed** - Runs on HuggingFace servers  
✅ **No VRAM limits** - Uses their infrastructure  
✅ **Free tier available** - Limited requests per hour  
✅ **Same results** - Uses same Mistral-7B model  

## Limitations

⚠️ **Rate limits** - Free tier has request limits  
⚠️ **Slower** - Network latency + cold start (~20s first request)  
⚠️ **Internet required** - Must be online  

## Alternative: Use Smaller Model Locally

If you want to run locally with 10GB VRAM:

```bash
# Download quantized 4-bit model (fits in 10GB)
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-AWQ --local-dir ~/models/mistral-7b-awq
```

Then update `src/postero_generalized.py` line 52:
```python
self.llm = LLM(
    self.llm_path,
    quantization="awq",  # 4-bit quantization
    gpu_memory_utilization=0.9
)
```

## Comparison

| Method | VRAM | Speed | Cost |
|--------|------|-------|------|
| Local Full | 16GB | Fast | Free |
| Local AWQ | 10GB | Fast | Free |
| HF API | 0GB | Slow | Free tier |

## Recommendation

**For your 10.56GB GPU:** Use HuggingFace API for now, or download AWQ quantized model for local inference.

---

**Quick Start:**
```bash
export HF_TOKEN="hf_..."
python3 test_postero_api.py
```
