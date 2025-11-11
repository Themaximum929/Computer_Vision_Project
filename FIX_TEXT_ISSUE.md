# Fix: Artificial Words Still Appearing

## Problem
Standard text removal wasn't catching all artificial text on posters.

## Solutions (3 Approaches)

### ✅ Solution 1: Use Aggressive Text Removal (RECOMMENDED)

```bash
# Generate new poster with aggressive text removal
python run_pipeline.py "your keywords" --lora --aggressive-text-removal
```

**What it does:**
- 3 detection methods (edges, adaptive threshold, MSER)
- Multiple edge detection thresholds
- Detects horizontal AND vertical text
- 2 inpainting passes
- Larger inpainting radius (20px vs 7px)

### ✅ Solution 2: Fix Existing Poster

```bash
# Clean up already generated poster
python fix_text_aggressive.py outputs/poster.png

# More passes for stubborn text
python fix_text_aggressive.py outputs/poster.png --iterations 5
```

### ✅ Solution 3: Prevent Text Generation

The negative prompt has been strengthened to prevent text in the first place:
- Added: `typography, font, title, subtitle, caption, writing, alphabet, numbers, symbols`
- Increased guidance scale: 7.5 → 8.5 (follows negative prompt better)

## Quick Comparison

| Method | Detection | Inpainting | Speed |
|--------|-----------|------------|-------|
| Standard | 1 method | 7px radius | Fast |
| Aggressive | 3 methods | 20px radius, 2 passes | Slower |

## Usage Examples

### Generate with Aggressive Removal
```bash
# Best option for clean posters
python run_pipeline.py "space adventure" --lora --aggressive-text-removal
```

### Fix Existing Image
```bash
# Quick fix
python fix_text_aggressive.py outputs/my_poster.png

# Extra aggressive (5 passes)
python fix_text_aggressive.py outputs/my_poster.png --iterations 5 --output outputs/my_poster_clean.png
```

### Batch Fix All Posters
```python
from pathlib import Path
from PIL import Image
from src.aggressive_text_remover import AggressiveTextRemover

remover = AggressiveTextRemover()

for img_path in Path("outputs").glob("*.png"):
    image = Image.open(img_path)
    cleaned, _ = remover.remove_text(image, iterations=3)
    cleaned.save(f"outputs/clean/{img_path.name}")
    print(f"Cleaned: {img_path.name}")
```

## What Changed

### 1. Stronger Negative Prompt
```python
# Before
"text, words, letters, watermark, ..."

# After
"text, words, letters, typography, font, title, subtitle, caption, 
 watermark, logo, signature, writing, alphabet, numbers, symbols, ..."
```

### 2. Higher Guidance Scale
```python
guidance_scale = 8.5  # was 7.5
# Follows negative prompt more strictly
```

### 3. Multi-Method Detection
```python
# Method 1: Canny edges (3 thresholds)
# Method 2: Adaptive thresholding
# Method 3: MSER (text-like regions)
# Detects: horizontal, vertical, curved text
```

### 4. Larger Inpainting
```python
radius = 20  # was 7
iterations = 2  # was 1
```

## Troubleshooting

**Still seeing text after aggressive removal?**
```bash
# Increase iterations
python fix_text_aggressive.py poster.png --iterations 10
```

**Text removal too aggressive (removing non-text)?**
```bash
# Use standard removal
python run_pipeline.py "keywords" --lora
# (without --aggressive-text-removal flag)
```

**Want to see what's being detected?**
Add this to `aggressive_text_remover.py`:
```python
# Save mask for debugging
cv2.imwrite("debug_mask.png", mask)
```

## Performance

- **Standard removal:** ~0.2-0.6s
- **Aggressive removal:** ~1-3s
- **Worth it:** Yes, for clean professional posters

## Recommendation

**For best results:**
1. Always use `--aggressive-text-removal` flag
2. If text still appears, run `fix_text_aggressive.py` with 5+ iterations
3. Consider retraining LoRA with more epochs (see STYLE_IMPROVEMENTS.md)

## Example Commands

```bash
# Generate clean poster (recommended)
python run_pipeline.py "dark fantasy warrior" --lora --aggressive-text-removal

# Fix existing poster
python fix_text_aggressive.py outputs/poster.png --iterations 5

# Generate without any text removal (for comparison)
python run_pipeline.py "dark fantasy warrior" --lora --no-text-removal
```

## Summary

✅ **Aggressive text removal** - 3 detection methods, 2 passes  
✅ **Stronger negative prompt** - Prevents text generation  
✅ **Higher guidance scale** - Better prompt following  
✅ **Fix existing images** - `fix_text_aggressive.py`  
✅ **Configurable iterations** - Up to 10 passes if needed  

Use `--aggressive-text-removal` flag for best results!
