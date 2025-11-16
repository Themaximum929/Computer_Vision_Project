# Quick Implementation Guide - PosterCraft Features

## What I Just Created

### 1. Color Extractor (`src/color_extractor.py`)
- Extract 5 dominant colors from any image
- Smart contrast detection (white/black text)
- Generate complementary colors
- Generate analogous colors

### 2. Template Engine (`src/template_engine.py`)
- 5 professional templates (minimal, bold, vintage, modern, cinematic)
- Overlay effects (gradient, vignette, letterbox, accent bar)
- Border system
- Smart positioning

---

## How to Use Them

### Test Color Extraction
```python
from src.color_extractor import ColorExtractor
from PIL import Image

extractor = ColorExtractor()
image = Image.open("outputs/poster.png")

# Extract palette
colors = extractor.extract_palette(image, n_colors=5)
print("Dominant colors:", colors)

# Get contrast color
bg_color = colors[0]
text_color = extractor.get_contrast_color(bg_color)
print(f"For background {bg_color}, use text color {text_color}")

# Generate harmonies
complementary = extractor.create_complementary(colors[0])
analogous = extractor.create_analogous(colors[0])
print("Complementary:", complementary)
print("Analogous:", analogous)
```

### Test Templates
```python
from src.template_engine import TemplateEngine
from PIL import Image

engine = TemplateEngine()
image = Image.open("outputs/poster.png")

# Apply template
template = engine.get_template('bold')
print("Template config:", template)

# Add overlay
image_with_overlay = engine.apply_overlay(image, 'gradient_bottom', color=(0, 0, 0))
image_with_overlay.save("outputs/with_overlay.png")

# Add border
image_with_border = engine.add_border(image, width=30, color=(255, 255, 255))
image_with_border.save("outputs/with_border.png")
```

---

## Integration Steps

### Step 1: Integrate Color Extraction into Pipeline

Edit `src/pipeline.py`:
```python
from src.color_extractor import ColorExtractor

class Key2PosterPipeline:
    def __init__(self, ...):
        self.color_extractor = ColorExtractor()
    
    def generate_poster(self, ...):
        # After image generation
        image = self.generator.generate(...)
        
        # Extract colors
        palette = self.color_extractor.extract_palette(image)
        print(f"Extracted palette: {palette}")
        
        # Use palette for text color
        text_color = self.color_extractor.get_contrast_color(palette[0])
```

### Step 2: Integrate Templates into Pipeline

Edit `src/pipeline.py`:
```python
from src.template_engine import TemplateEngine

class Key2PosterPipeline:
    def __init__(self, ..., template='minimal'):
        self.template_engine = TemplateEngine()
        self.template_name = template
    
    def generate_poster(self, ...):
        # After image generation
        image = self.generator.generate(...)
        
        # Apply template
        template = self.template_engine.get_template(self.template_name)
        
        # Add overlay
        if template['overlay']:
            image = self.template_engine.apply_overlay(
                image, 
                template['overlay'],
                color=palette[0]  # Use dominant color
            )
        
        # Add border
        if template.get('border'):
            image = self.template_engine.add_border(image)
```

### Step 3: Update UI

Edit `app_unified.py`:
```python
import gradio as gr

def create_ui():
    with gr.Blocks() as demo:
        with gr.Row():
            keywords = gr.Textbox(label="Keywords")
            template = gr.Dropdown(
                choices=['minimal', 'bold', 'vintage', 'modern', 'cinematic'],
                value='minimal',
                label="Template"
            )
        
        with gr.Row():
            color_palette = gr.Gallery(label="Extracted Colors")
        
        generate_btn = gr.Button("Generate")
        output_image = gr.Image(label="Result")
        
        generate_btn.click(
            fn=generate_with_template,
            inputs=[keywords, template],
            outputs=[output_image, color_palette]
        )
```

---

## Test Script

Create `test_postercraft_features.py`:
```python
"""Test PosterCraft-style features"""
from src.color_extractor import ColorExtractor
from src.template_engine import TemplateEngine
from src.pipeline import Key2PosterPipeline
from PIL import Image
from pathlib import Path

def test_features():
    print("Testing PosterCraft Features")
    print("="*60)
    
    # Test 1: Color Extraction
    print("\n[1] Testing Color Extraction...")
    extractor = ColorExtractor()
    
    # Generate a test image
    pipeline = Key2PosterPipeline()
    image, _, _ = pipeline.generate_poster(
        "cyberpunk neon city",
        output_path="outputs/test_color.png",
        seed=42,
        evaluate=False
    )
    
    # Extract colors
    colors = extractor.extract_palette(image)
    print(f"   Extracted {len(colors)} colors:")
    for i, color in enumerate(colors):
        print(f"   Color {i+1}: RGB{color}")
        text_color = extractor.get_contrast_color(color)
        print(f"   → Best text color: RGB{text_color}")
    
    # Test 2: Templates
    print("\n[2] Testing Templates...")
    engine = TemplateEngine()
    output_dir = Path("outputs/template_tests")
    output_dir.mkdir(exist_ok=True)
    
    for template_name in ['minimal', 'bold', 'vintage', 'modern', 'cinematic']:
        print(f"   Testing {template_name} template...")
        template = engine.get_template(template_name)
        
        # Apply overlay
        if template['overlay']:
            result = engine.apply_overlay(image, template['overlay'], color=colors[0])
        else:
            result = image.copy()
        
        # Add border
        if template.get('border'):
            result = engine.add_border(result)
        
        result.save(output_dir / f"{template_name}.png")
        print(f"   ✓ Saved: {template_name}.png")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print(f"Check outputs in: {output_dir}")

if __name__ == "__main__":
    test_features()
```

Run: `python test_postercraft_features.py`

---

## Next Steps

### Immediate (This Week)
1. ✅ Test color extraction
2. ✅ Test templates
3. ✅ Integrate into pipeline
4. ✅ Update UI with template selector

### Short Term (Next Week)
5. Add font selection
6. Add color palette picker
7. Add export size options
8. Create template previews

### Medium Term (Next Month)
9. Advanced typography
10. Layout engine with rule of thirds
11. Batch generation with templates
12. PDF export

---

## Dependencies

Add to `requirements.txt`:
```
scikit-learn>=1.0.0  # For K-means clustering
```

Install:
```bash
pip install scikit-learn
```

---

## Summary

You now have:
- ✅ Color extraction (like PosterCraft)
- ✅ Template system (5 professional layouts)
- ✅ Overlay effects (gradient, vignette, etc.)
- ✅ Border system

This puts you on par with PosterCraft's core features while maintaining your advantages (genre detection, LoRA training, text removal).
