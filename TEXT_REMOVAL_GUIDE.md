# Text Removal Guide

## Problem
Generated posters sometimes contain artificial text/words that shouldn't be there.

## Solution
Added **Agent 3: Text Remover** that automatically detects and removes text using inpainting.

## How It Works

1. **Text Detection**
   - Edge detection (Canny)
   - Morphological operations to connect text
   - Contour filtering (horizontal, small height, reasonable size)

2. **Text Removal**
   - OpenCV inpainting (TELEA algorithm)
   - Fills text regions with surrounding content
   - Preserves image quality

## Usage

### Automatic (Default)
Text removal is **enabled by default** in the pipeline:

```bash
# Text removal happens automatically
python run_pipeline.py "space adventure" --lora
```

### Disable Text Removal
```bash
# Skip text removal if you want to keep text
python run_pipeline.py "space adventure" --lora --no-text-removal
```

### Remove Text from Existing Image
```bash
# Clean up an already generated poster
python remove_text_from_image.py outputs/poster.png

# Specify output path
python remove_text_from_image.py outputs/poster.png --output outputs/poster_clean.png
```

## Pipeline Integration

The text remover is now **Agent 3** in the 5-agent system:

```
Agent 1: Concept Expander → Creative Brief
Agent 2: Visual Designer → Raw Image
Agent 3: Text Remover → Text-Free Image  ← NEW
Agent 4: Quality Refiner → Enhanced Image
Agent 5: Quality Evaluator → Quality Metrics
```

## Technical Details

### Detection Parameters
```python
# Text characteristics
aspect_ratio > 2      # Wide and short
100 < area < 50000    # Reasonable size
height < 100          # Not too tall
```

### Inpainting
- **Algorithm:** TELEA (Fast Marching Method)
- **Radius:** 7 pixels
- **Speed:** ~0.1-0.5 seconds per image

## Examples

### Before Text Removal
```
[Poster with "ADVENTURE" text overlay]
```

### After Text Removal
```
[Clean poster without text]
```

## Limitations

1. **May miss very small text** (< 100 pixels area)
2. **May miss vertical text** (aspect ratio filter)
3. **May detect non-text patterns** (rare false positives)
4. **Inpainting quality** depends on surrounding content

## Troubleshooting

**Issue:** Text not detected  
**Solution:** Text might be too small or vertical. Adjust parameters in `src/text_remover.py`:
```python
# Make detection more aggressive
if aspect_ratio > 1.5 and 50 < area < 100000 and h < 150:
```

**Issue:** Non-text regions removed  
**Solution:** Make detection more conservative:
```python
# Stricter filtering
if aspect_ratio > 3 and 200 < area < 30000 and h < 80:
```

**Issue:** Inpainting looks bad  
**Solution:** Increase inpainting radius:
```python
inpainted = cv2.inpaint(img_array, mask, 10, cv2.INPAINT_TELEA)  # was 7
```

## Installation

Make sure OpenCV is installed:
```bash
pip install opencv-python>=4.8.0
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

## Performance

- **Detection:** ~0.05 seconds
- **Inpainting:** ~0.1-0.5 seconds
- **Total overhead:** ~0.2-0.6 seconds per poster
- **Minimal impact** on generation time

## Advanced Usage

### Programmatic Usage
```python
from src.text_remover import TextRemover
from PIL import Image

remover = TextRemover()
image = Image.open("poster.png")
cleaned, text_found = remover.remove_text(image)

if text_found:
    cleaned.save("poster_clean.png")
```

### Batch Processing
```python
from pathlib import Path
from src.text_remover import TextRemover
from PIL import Image

remover = TextRemover()

for img_path in Path("outputs").glob("*.png"):
    image = Image.open(img_path)
    cleaned, text_found = remover.remove_text(image)
    if text_found:
        cleaned.save(f"{img_path.stem}_clean.png")
        print(f"Cleaned: {img_path.name}")
```

## Integration with Experiments

Text removal is automatically applied in experiments:

```bash
python src/experiment.py  # Text removal enabled for all generations
```

To compare with/without text removal:
```python
# With text removal (default)
pipeline = Key2PosterPipeline(use_lora=True, remove_text=True)

# Without text removal
pipeline = Key2PosterPipeline(use_lora=True, remove_text=False)
```

## Summary

✅ **Automatic text detection and removal**  
✅ **Enabled by default**  
✅ **Fast (~0.2-0.6s overhead)**  
✅ **Can be disabled with --no-text-removal**  
✅ **Works on existing images**  
✅ **Integrated as Agent 3**  

The text removal mechanism ensures your generated posters are clean and professional-looking!
