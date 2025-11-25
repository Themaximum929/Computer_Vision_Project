# Deploy to Hugging Face Spaces

## Quick Steps

### 1. Create Space
- Go to: https://huggingface.co/new-space
- Name: `key2poster-flux`
- SDK: **Gradio**
- Hardware: **ZeroGPU** (free A100 40GB)
- Click "Create Space"

### 2. Prepare Files

Rename and copy:
```bash
# Rename app
copy app_hf.py app.py

# Files needed:
- app.py (renamed from app_hf.py)
- requirements.txt
- src/ (entire folder)
- fonts/ (if exists)
```

### 3. Upload via Web

**Option A: Drag & Drop**
1. Go to your Space's "Files" tab
2. Drag files/folders into browser
3. Commit changes

**Option B: Git Command Line**
```bash
# Install Git LFS first: https://git-lfs.github.com/

# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/key2poster-flux
cd key2poster-flux

# Copy files
copy ..\app_hf.py app.py
copy ..\requirements.txt .
xcopy ..\src src\ /E /I
xcopy ..\fonts fonts\ /E /I

# Push
git add .
git commit -m "Initial deployment"
git push
```

### 4. Configure Space

Create `README.md` in your space:
```yaml
---
title: Key2Poster FLUX
emoji: 🎨
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# Key2Poster FLUX
Generate professional posters from 2-5 keywords using FLUX.1
```

### 5. Wait for Build

- Space will automatically build (~5-10 min)
- Check logs in "Logs" tab
- Once ready, your app will be live!

## Requirements

Make sure `requirements.txt` has:
```
spaces
gradio>=4.0.0
torch
diffusers
transformers
accelerate
pillow
numpy
textblob
```

## ZeroGPU Notes

- Free A100 40GB GPU
- Auto-allocated on request
- 60s timeout per generation
- Perfect for FLUX inference

## Troubleshooting

**Build fails?**
- Check logs in Space
- Verify all files uploaded
- Check requirements.txt syntax

**Slow generation?**
- ZeroGPU should be 5-10s
- Check if GPU is allocated in logs

**Out of memory?**
- Disable genre_lora in app_hf.py
- Reduce image size if needed
