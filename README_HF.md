# Deploy to Hugging Face Spaces (ZeroGPU)

## Quick Deploy

1. Create a new Space on Hugging Face: https://huggingface.co/new-space
2. Select **Gradio** SDK and **ZeroGPU** hardware
3. Upload these files:
   - `app_hf.py` (rename to `app.py`)
   - `requirements.txt`
   - `src/` folder (entire directory)
   - `fonts/` folder (if using text overlay)

## Requirements for HF Space

Add to `requirements.txt`:
```
spaces
gradio
torch
diffusers
transformers
pillow
numpy
```

## ZeroGPU Benefits

- **Free GPU access** (A100 40GB)
- **Fast inference** (~5-10s per image)
- **Auto-scaling** (GPU allocated on-demand)
- **No VRAM limits** (40GB available)

## Configuration

The `@spaces.GPU(duration=60)` decorator:
- Requests GPU for 60 seconds
- Automatically releases after generation
- Handles multiple concurrent users

## Local Speed Fix

Your local slowness is from CPU offloading. I've removed it - restart your app:

```bash
python app_flux.py
```

Should now be **10-20s** instead of 460s!
