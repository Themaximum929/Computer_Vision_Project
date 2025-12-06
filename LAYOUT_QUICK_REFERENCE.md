# Layout & Composition: Quick Reference Card

## 🎯 Three Methods at a Glance

| | Template | LayoutGAN | PosterO |
|---|---|---|---|
| **Speed** | 10s ⚡⚡⚡ | 19s ⚡⚡ | 28s ⚡ |
| **Quality** | 0.75 ⭐⭐⭐ | 0.78 ⭐⭐⭐⭐ | 0.84 ⭐⭐⭐⭐⭐ |
| **Adaptivity** | Fixed | Optimized | Content-Aware |
| **Best For** | Batch | Varied | Premium |

## 📊 Key Metrics Comparison

```
Quality Scores (0-1, higher is better):

Alignment:    ████████████████████ 0.92 (PosterO)
              ████████████████▓▓▓▓ 0.89 (Template)
              ███████████████▓▓▓▓▓ 0.85 (LayoutGAN)

Readability:  ████████████████▓▓▓▓ 0.80 (PosterO)
              ██████████████▓▓▓▓▓▓ 0.75 (LayoutGAN)
              █████████████▓▓▓▓▓▓▓ 0.71 (Template)

Balance:      ████████████████▓▓▓▓ 0.83 (PosterO)
              ███████████████▓▓▓▓▓ 0.81 (LayoutGAN)
              █████████████▓▓▓▓▓▓▓ 0.76 (Template)
```

## 🔧 Quick Usage

### Template Mode
```python
from src.pipeline import Key2PosterPipeline

pipeline = Key2PosterPipeline(use_template=True)
image, brief, metrics = pipeline.generate_poster(
    keywords="cyberpunk city",
    poster_type='movie',
    style_preset='cinematic'
)
```

### LayoutGAN Mode
```python
pipeline = Key2PosterPipeline(auto_template=True)
image, brief, metrics = pipeline.generate_poster(
    keywords="music festival",
    poster_type='event'
)
```

### PosterO Mode
```python
from src.pipeline_postero import Key2PosterPosterO

pipeline = Key2PosterPosterO()
image, brief, metrics = pipeline.generate_poster(
    keywords="vintage travel",
    poster_type='movie'
)
```

## 📐 Layout Patterns (Template Mode)

```
SPLIT           GRID            HERO
┌─────────┐     ┌─────────┐     ┌─────────┐
│  IMAGE  │     │  IMAGE  │     │         │
├─────────┤     │         │     │  IMAGE  │
│  TEXT   │     ├─────────┤     │         │
└─────────┘     │  TEXT   │     ├─────────┤
                └─────────┘     │  TEXT   │
                                └─────────┘

SIDEBAR         ASYMMETRIC      MINIMAL
┌────┬────┐     ┌─────────┐     ┌─────────┐
│    │TEXT│     │ ┌─────┐ │     │         │
│IMG │    │     │ │IMAGE│ │     │  IMAGE  │
│    │    │     │ └─────┘ │     │         │
└────┴────┘     │  TEXT   │     │         │
                └─────────┘     │  TEXT   │
                                └─────────┘
```

## 🎨 Design Constraints

### All Methods Apply:
- ✅ 50px minimum borders
- ✅ 30% target text coverage
- ✅ 4.5:1 contrast ratio (WCAG)
- ✅ Title above captions
- ✅ No text-image overlap

### LayoutGAN Adds:
- ✅ IoU < 0.1 between elements
- ✅ 10px grid alignment
- ✅ Visual balance optimization

### PosterO Adds:
- ✅ Content-aware positioning
- ✅ Face/object avoidance
- ✅ Automatic underlay detection

## 🚀 Run Evaluation

```bash
# Quick demo (2 minutes)
python demo_evaluation.py
python visualize_evaluation.py

# Full evaluation (30 minutes, requires GPU)
python run_comparative_evaluation.py
python visualize_evaluation.py
```

## 📈 Expected Results

```
Method      Alignment  Overlap  Balance  Time
─────────────────────────────────────────────
Template    0.892      0.043    0.756    10s
LayoutGAN   0.847      0.067    0.812    19s
PosterO     0.923      0.018    0.834    28s
```

## 🔑 Key Innovations

1. **CLG-LO** (LayoutGAN): Constraint-based optimization
   - 50 iterations of gradient descent
   - Multi-objective loss function
   - Differentiable constraints

2. **Content-Aware** (PosterO): CNN + LLM pipeline
   - Stage 1: Detect available areas
   - Stage 2: Generate SVG layout
   - 58% overlap reduction

3. **Dynamic Contrast**: Automatic color adjustment
   - Sample background color
   - Ensure readability
   - WCAG compliance

## 📚 Documentation

- **Full Report**: [LAYOUT_COMPOSITION_REPORT.md](LAYOUT_COMPOSITION_REPORT.md)
- **Summary**: [LAYOUT_SUMMARY.md](LAYOUT_SUMMARY.md)
- **Evaluation**: [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md)
- **Main README**: [README.md](README.md)

## 🎓 Academic References

- **PosterO**: CVPR 2025 (Content-Aware AI Layout)
- **LayoutGAN**: CVPR 2019 (Generative Layout)
- **FLUX.1**: Black Forest Labs 2024 (Image Generation)

## 💡 Decision Tree

```
Need batch processing (100+ posters)?
├─ YES → Use Template Mode
└─ NO → Need highest quality?
    ├─ YES → Use PosterO Mode
    └─ NO → Use LayoutGAN Mode
```

## ⚡ Performance Tips

1. **Template**: Use for production (fastest)
2. **LayoutGAN**: Balance speed/quality
3. **PosterO**: Premium applications only
4. **Batch**: Process in parallel (3× speedup)
5. **Memory**: Clear CUDA cache between runs

## 🐛 Common Issues

**"Dimensions not divisible by 8"**
→ Fixed in v3.0+ (auto-rounding)

**"Text overlaps image"**
→ Use PosterO Mode (content-aware)

**"Generation too slow"**
→ Use Template Mode (3× faster)

**"Low contrast text"**
→ Enable dynamic contrast (default ON)

---

**Quick Start**: `python app_unified.py` → Select mode → Generate!
