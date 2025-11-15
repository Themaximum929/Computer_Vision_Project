# Smart Text Overlay System

## Professional Movie Poster Text Placement

The new `SmartTextOverlay` system analyzes your generated image and intelligently places text like professional movie posters.

---

## Key Features

### 1. **Intelligent Position Detection**
Analyzes image regions to find the best text placement:
- ✅ Detects low-detail areas (good for text)
- ✅ Finds uniform brightness regions
- ✅ Avoids busy/complex areas
- ✅ Considers edge density

### 2. **Automatic Contrast Adjustment**
- Dark background → White text
- Light background → Black text
- Automatic color adjustment for readability

### 3. **Professional Styling**
- Multi-layer shadows for depth
- Stroke/outline for clarity
- Optional background bars for busy images
- Genre-specific fonts and colors

### 4. **Region Analysis**
Divides image into 7 regions:
- Top, Middle, Bottom
- Top-left, Top-right
- Bottom-left, Bottom-right

Scores each region based on:
- Brightness (40-200 = good)
- Edge density (< 10% = good)
- Contrast (< 50 = uniform)

---

## How It Works

### Step 1: Image Analysis
```python
# Analyzes image regions
regions = {
    'top': score_85,      # Clear sky
    'middle': score_30,   # Busy action
    'bottom': score_75    # Dark ground
}
```

### Step 2: Position Selection
```python
# Chooses best position
if style_preference == 'bottom' and bottom_score > 60:
    position = 'bottom'
else:
    position = highest_scoring_region
```

### Step 3: Text Styling
```python
# Applies professional styling
- Shadow: Multi-layer for depth
- Stroke: Outline for clarity
- Color: Adjusted for contrast
- Background: Added if needed
```

---

## Examples

### Example 1: Action Poster
```
Image: Explosion in middle, clear sky at top
Analysis: Top region score = 90 (clear, uniform)
Result: Title placed at top with white text
```

### Example 2: Dark Horror
```
Image: Dark throughout, slightly lighter at bottom
Analysis: Bottom region score = 70 (darkest area)
Result: Title at bottom with white text + glow
```

### Example 3: Busy Composition
```
Image: Complex details everywhere
Analysis: All regions score < 60
Result: Adds semi-transparent background bar
```

---

## Comparison

### Old Text Overlay
```python
# Simple placement
- Always bottom center
- Fixed color
- No image analysis
- Can be unreadable
```

### Smart Text Overlay
```python
# Intelligent placement
- Analyzes 7 regions
- Adjusts color for contrast
- Avoids busy areas
- Always readable
```

---

## Usage

```bash
# Automatic smart placement
python run_pipeline.py "space adventure" --genre-lora --add-title

# The system will:
# 1. Generate poster
# 2. Analyze image regions
# 3. Find best text position
# 4. Apply professional styling
# 5. Ensure readability
```

---

## Technical Details

### Region Scoring Algorithm
```python
score = 0
if 40 < brightness < 200:  # Good contrast
    score += 30
if edge_density < 0.1:     # Low detail
    score += 40
if contrast < 50:          # Uniform
    score += 30

# Total score: 0-100
# > 60 = Good for text
# < 60 = Add background bar
```

### Color Adjustment
```python
if brightness < 100:    # Dark background
    text_color = white
elif brightness > 180:  # Light background
    text_color = black
else:                   # Use genre color
    text_color = style_color
```

### Shadow Depth
```python
# Multi-layer shadow for 3D effect
for offset in range(shadow_offset, 0, -1):
    alpha = base_alpha * (offset / max_offset)
    draw_shadow(offset, alpha)
```

---

## Genre-Specific Styling

### Action
- **Position:** Top (if clear) or Bottom
- **Color:** Red with black stroke
- **Shadow:** Heavy, 6px offset
- **Font:** Impact, bold

### Horror
- **Position:** Center (dramatic)
- **Color:** Dark red
- **Shadow:** Large, 8px offset
- **Font:** Impact

### Sci-Fi
- **Position:** Bottom
- **Color:** Cyan with glow
- **Shadow:** Blue glow effect
- **Font:** Arial, wide spacing

### Drama
- **Position:** Bottom
- **Color:** White, elegant
- **Shadow:** Subtle, 3px
- **Font:** Times, serif

---

## Advanced Features

### 1. Background Bar
When image is too busy (score < 60):
```python
# Adds semi-transparent bar
draw.rectangle(
    [0, text_y - 20, width, text_y + height + 20],
    fill=(0, 0, 0, 150)  # 60% transparent black
)
```

### 2. Multi-Layer Shadow
Creates depth like professional posters:
```python
# 3 shadow layers
Layer 1: offset=6, alpha=200 (darkest)
Layer 2: offset=4, alpha=133
Layer 3: offset=2, alpha=66  (lightest)
```

### 3. Stroke Outline
Ensures text is readable on any background:
```python
# Outline around text
stroke_width = 3
stroke_color = black
```

---

## Results

**Before (Simple Overlay):**
- Text always at bottom
- Fixed white color
- Sometimes unreadable
- Looks amateur

**After (Smart Overlay):**
- Text in optimal position
- Adjusted for contrast
- Always readable
- Looks professional

---

## Summary

The Smart Text Overlay system:
1. ✅ Analyzes image composition
2. ✅ Finds best text position
3. ✅ Adjusts colors for contrast
4. ✅ Applies professional styling
5. ✅ Ensures readability

**Result:** Movie poster-quality text placement automatically! 🎨
