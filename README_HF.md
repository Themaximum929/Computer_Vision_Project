---
title: Key2Poster FLUX
emoji: 🎨
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 4.44.0
app_file: app_hf.py
pinned: false
license: mit
python_version: 3.10
---

# Key2Poster: AI Poster Generator

Generate professional posters from 2-5 keywords using **FLUX.1-schnell** with native text rendering.

## Features

✅ **FLUX.1 Text Generation** - Native text rendering (no PIL overlay)  
✅ **7 Poster Types** - Movie, Advertise, Event, Education, Social, Music, Sports  
✅ **7 Style Presets** - Cinematic, Minimalist, Neon, Dark, Vintage, Bright, Professional  
✅ **Multi-Agent System** - 7 specialized agents for quality output  
✅ **Aesthetic Scoring** - Automated quality evaluation  

## Usage

1. Enter 2-5 keywords (e.g., "cyberpunk neon city")
2. Select poster type and style preset
3. Click "Generate Poster"
4. Download your professional poster!

## Examples

- **Movie:** "space exploration adventure" + Cinematic style
- **Event:** "summer music festival" + Bright style
- **Advertise:** "fresh organic food" + Professional style
- **Social:** "save the ocean" + Minimalist style

## Models

- **FLUX.1-schnell** - Fast text generation (4-step inference)
- **Genre Classifier** - Auto-detect content genre
- **Aesthetic Scorer** - Quality evaluation

## Performance

- Generation time: ~10-20s on GPU
- Image size: 1024x1024
- Text: Natively rendered by FLUX

---

Built with ❤️ using FLUX.1 and Gradio
