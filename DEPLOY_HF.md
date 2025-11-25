# Deploy to Hugging Face Spaces

## Quick Deploy

1. **Create HF Space**
   ```bash
   # Go to https://huggingface.co/new-space
   # Name: key2poster-flux
   # SDK: Gradio
   # Hardware: GPU (T4 or better recommended)
   ```

2. **Clone and Push**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/key2poster-flux
   cd key2poster-flux
   
   # Copy files
   cp app_hf.py app.py
   cp requirements_hf.txt requirements.txt
   cp README_HF.md README.md
   cp -r src/ .
   
   # Push to HF
   git add .
   git commit -m "Initial commit"
   git push
   ```

3. **Configure Space**
   - Go to Space settings
   - Select GPU hardware (T4 minimum)
   - Enable persistent storage (optional)
   - Set secrets if needed

## Files for HF Space

- `app_hf.py` → Main application (rename to `app.py`)
- `requirements_hf.txt` → Dependencies (rename to `requirements.txt`)
- `README_HF.md` → Space README (rename to `README.md`)
- `.gitattributes` → Git LFS configuration
- `src/` → Source code directory

## Hardware Requirements

| Hardware | Performance | Cost |
|----------|-------------|------|
| CPU | ~2-3 min/image | Free |
| T4 (16GB) | ~15-20s/image | $0.60/hr |
| A10G (24GB) | ~10-15s/image | $3.15/hr |

**Recommended:** T4 GPU for good balance of speed and cost

## Environment Variables (Optional)

```bash
# In Space settings → Variables and secrets
HF_TOKEN=your_token_here  # If using private models
GRADIO_ANALYTICS_ENABLED=False
```

## Optimization Tips

1. **Model Caching:** Models auto-download to HF cache
2. **Queue System:** `demo.queue()` handles concurrent users
3. **Memory Management:** Disable unused features (LoRA, super-resolution)
4. **Batch Size:** Keep at 1 for memory efficiency

## Testing Locally

```bash
# Test before deploying
python app_hf.py

# Should open at http://localhost:7860
```

## Troubleshooting

**Out of Memory:**
- Reduce image size in pipeline
- Disable super-resolution
- Use CPU offloading

**Slow Loading:**
- Models download on first run (~23GB for FLUX)
- Subsequent runs use cached models

**Import Errors:**
- Ensure all `src/` files are included
- Check requirements.txt has all dependencies

## Post-Deploy

1. Test with example inputs
2. Monitor Space logs for errors
3. Share your Space URL!

---

**Example Space URL:** `https://huggingface.co/spaces/YOUR_USERNAME/key2poster-flux`
