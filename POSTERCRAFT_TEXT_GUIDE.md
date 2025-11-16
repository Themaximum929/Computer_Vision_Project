# PosterCraft Text Design Analysis

## What Makes PosterCraft Text Aesthetic

### 1. Gradient Overlays
**Purpose:** Ensure text readability without obscuring the image

```python
# PosterCraft approach
for i in range(height * 0.3):
    alpha = int(180 * (i / (height * 0.3)))
    draw.rectangle([(0, h - i), (w, h)], fill=(0, 0, 0, alpha))
```

**Key Points:**
- Gradual fade from transparent to semi-opaque
- Covers 30-40% of bottom area
- Alpha ranges from 0 to 160-200
- Genre-specific intensity

### 2. Text Hierarchy
**Structure:**
```
Tagline (small, subtle)
    ↓
Title (large, bold)
    ↓
Credits (tiny, bottom)
```

**Font Sizes:**
- Tagline: 2-3% of height
- Title: 8-10% of height
- Credits: 1.5-2% of height

### 3. Color Harmony
**PosterCraft extracts colors from the image:**

```python
# Extract dominant colors
palette = extract_palette(image)

# Use complementary color for text
text_color = get_complementary(palette[0])

# Or use accent color
text_color = palette[1]  # Second most dominant
```

**Genre-Specific Colors:**
- Action: Red (#FF3232)
- Horror: Dark Red (#C80000)
- Sci-Fi: Cyan (#00C8FF)
- Romance: Pink (#FF96C8)
- Comedy: Yellow (#FFDC00)
- Fantasy: Gold (#FFD700)

### 4. Text Effects
**Layering:**
```
1. Shadow (offset +3px, black with 70% opacity)
2. Outline (8-direction, 2px, black)
3. Main text (genre color or white)
```

**Implementation:**
```python
# Shadow
draw.text((x+3, y+3), text, font=font, fill=(0,0,0,180))

# Outline (8 directions)
for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2), (-2,0), (2,0), (0,-2), (0,2)]:
    draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0))

# Main
draw.text((x, y), text, font=font, fill=color)
```

### 5. Font Selection
**PosterCraft uses:**
- **Title:** Bebas Neue (bold, condensed, uppercase)
- **Subtitle:** Montserrat Bold (modern, clean)
- **Body:** Montserrat Regular (readable)

**Why these work:**
- High contrast (thick vs thin)
- Professional appearance
- Excellent readability
- Wide character spacing

### 6. Positioning Strategy
**Safe Zones:**
```
Top 15%:     Avoid (usually important visual)
Middle 50%:  Avoid (main subject)
Bottom 35%:  Safe for text
```

**Optimal Positions:**
- Title: 80-85% from top
- Tagline: 75-78% from top
- Credits: 92-95% from top

### 7. Spacing & Kerning
**Letter Spacing:**
- Title: +5-10% (wider for impact)
- Tagline: Normal
- Credits: +2-5% (slightly wider)

**Line Height:**
- Title: 1.0 (tight)
- Tagline: 1.2 (comfortable)
- Credits: 1.1 (compact)

## Implementation in Key2Poster

### Basic Usage
```python
from src.aesthetic_text_overlay import AestheticTextOverlay

overlay = AestheticTextOverlay()

# Full poster text
image = overlay.add_poster_text(
    image=image,
    title="Cyberpunk City",
    genre="scifi",
    tagline="The future is now",
    credits="Directed by John Doe"
)

# Minimal text
image = overlay.add_minimal_text(
    image=image,
    title="Cyberpunk City",
    accent_color=(0, 200, 255)
)
```

### With Color Extraction
```python
from src.color_palette_extractor import ColorPaletteExtractor
from src.aesthetic_text_overlay import AestheticTextOverlay

# Extract colors
extractor = ColorPaletteExtractor()
palette = extractor.extract_palette(image)
accent = extractor.get_accent_color()

# Apply text with accent color
overlay = AestheticTextOverlay()
image = overlay.add_minimal_text(image, "Title", accent_color=accent)
```

### Genre-Specific Styling
```python
genres = ["action", "horror", "scifi", "romance", "comedy", "fantasy"]

for genre in genres:
    image = overlay.add_poster_text(
        image=base_image.copy(),
        title="Movie Title",
        genre=genre,
        tagline="Genre-specific styling"
    )
    image.save(f"poster_{genre}.png")
```

## Comparison: Before vs After

### Before (Original Key2Poster)
```python
# Simple text overlay
draw.text((x, y), title, font=font, fill=(255, 255, 255))
```
**Issues:**
- No gradient background
- Fixed white color
- No hierarchy
- Basic shadow only

### After (PosterCraft-Inspired)
```python
# Aesthetic text overlay
image = overlay.add_poster_text(
    image=image,
    title=title,
    genre=genre,
    tagline=tagline,
    credits=credits
)
```
**Improvements:**
- ✅ Gradient overlay for readability
- ✅ Genre-specific colors
- ✅ Text hierarchy (title/tagline/credits)
- ✅ Professional shadows and outlines
- ✅ Smart positioning

## Manual Customization

### Custom Gradient
```python
# In aesthetic_text_overlay.py, modify _add_gradient_overlay:

# Stronger gradient
for i in range(int(h * 0.5)):  # Increase from 0.35 to 0.5
    alpha = int(220 * (i / (h * 0.5)))  # Increase from 160 to 220
    draw.rectangle([(0, h - i), (w, h)], fill=(0, 0, 0, alpha))
```

### Custom Colors
```python
# Add to colors dict in _add_title:
colors = {
    "action": (255, 50, 50),
    "horror": (200, 0, 0),
    "scifi": (0, 200, 255),
    "custom": (100, 255, 100),  # Add your color
}
```

### Custom Fonts
```python
# Add to font_paths in __init__:
self.font_paths = {
    "title": "fonts/cinematic/YourFont.ttf",
    "subtitle": "fonts/cinematic/YourSubtitle.ttf",
    "tagline": "fonts/cinematic/YourTagline.ttf",
}
```

### Custom Positioning
```python
# Modify positions in _add_title:
y = int(h * 0.70)  # Move title higher (default: 0.82)

# Modify in _add_tagline:
y = int(h * 0.65)  # Move tagline higher (default: 0.76)
```

## Best Practices

### 1. Always Use Gradient
```python
# Bad
draw.text((x, y), title, fill=(255, 255, 255))

# Good
image = overlay.add_poster_text(image, title, genre)
```

### 2. Match Colors to Genre
```python
# Extract genre
genre = classifier.classify(keywords)

# Use genre-specific styling
image = overlay.add_poster_text(image, title, genre=genre)
```

### 3. Use Text Hierarchy
```python
# Full hierarchy
image = overlay.add_poster_text(
    image=image,
    title="Main Title",
    genre="scifi",
    tagline="Compelling tagline",
    credits="Director • Studio • Year"
)
```

### 4. Consider Image Brightness
```python
# For dark images
image = overlay.add_poster_text(image, title, genre)  # Standard

# For bright images
# Increase gradient strength manually or use darker text
```

## Testing

```bash
# Test aesthetic text overlay
python -c "
from PIL import Image
from src.aesthetic_text_overlay import AestheticTextOverlay

img = Image.open('outputs/test.png')
overlay = AestheticTextOverlay()
result = overlay.add_poster_text(img, 'Test Title', 'scifi', 'Amazing tagline')
result.save('outputs/aesthetic_test.png')
"
```

## Summary

**PosterCraft's aesthetic text design comes from:**
1. ✅ Gradient overlays (readability)
2. ✅ Text hierarchy (title/tagline/credits)
3. ✅ Color harmony (genre-specific)
4. ✅ Professional effects (shadow/outline)
5. ✅ Smart positioning (safe zones)
6. ✅ Font selection (Bebas Neue + Montserrat)
7. ✅ Proper spacing (letter spacing + line height)

**Now implemented in:** `src/aesthetic_text_overlay.py`
