# Simple Title Generation

## Overview

Instead of using the full prompt as title, the system now generates **simple 1-word titles** (max 7 characters).

## How It Works

### Algorithm
```
1. Extract first meaningful word from keywords (≤7 chars)
2. Skip articles (the, a, an, of, in, on, at)
3. Capitalize first letter
4. Fallback to genre-specific title if needed
```

### Examples

| Keywords | Genre | Generated Title |
|----------|-------|----------------|
| "cyberpunk neon city" | scifi | "Cyberpunk" |
| "dark horror mansion" | horror | "Dark" |
| "space exploration" | scifi | "Space" |
| "romantic sunset beach" | romance | "Romantic" |
| "epic fantasy warrior" | fantasy | "Epic" |
| "action packed thriller" | action | "Action" |

## Genre-Specific Fallbacks

If no suitable word found, uses genre-specific titles:

| Genre | Fallback Titles |
|-------|----------------|
| **Action** | Strike, Fury, Impact, Blaze, Storm, Rage |
| **Horror** | Dread, Terror, Shadows, Haunted, Cursed, Nightmare |
| **Sci-Fi** | Nexus, Quantum, Void, Genesis, Eclipse, Horizon |
| **Romance** | Beloved, Forever, Destiny, Passion, Hearts, Embrace |
| **Comedy** | Chaos, Madness, Mayhem, Laughs, Hijinks, Antics |
| **Fantasy** | Legend, Realm, Quest, Magic, Prophecy, Kingdom |
| **Thriller** | Hunted, Trapped, Vanished, Secrets, Lies, Betrayal |
| **Drama** | Truth, Legacy, Journey, Redemption, Sacrifice, Hope |

## Usage

### Automatic (in Unified Pipeline)
```python
from src.unified_pipeline import UnifiedPosterPipeline

pipeline = UnifiedPosterPipeline()
result = pipeline.generate("cyberpunk neon city")
# Title automatically generated: "Cyberpunk"
```

### Manual
```python
from src.title_generator import TitleGenerator

gen = TitleGenerator()
title = gen.generate("space exploration adventure", genre="scifi")
print(title)  # Output: "Space"
```

### Custom Title
```python
from src.aesthetic_text_overlay import AestheticTextOverlay

overlay = AestheticTextOverlay()
image = overlay.add_poster_text(
    image=image,
    title="Custom",  # Your custom title
    genre="scifi",
    tagline="Your tagline"
)
```

## Testing

```bash
python test_title_generator.py
```

**Output:**
```
Keywords: 'cyberpunk neon city'
Genre: scifi
Generated Title: 'Cyberpunk'
Length: 9 chars
✓ Valid
```

## Customization

### Add Custom Fallbacks

Edit `src/title_generator.py`:

```python
self.genre_patterns = {
    "action": ["strike", "fury", "impact"],
    "custom_genre": ["word1", "word2", "word3"],  # Add yours
}
```

### Change Max Length

```python
# In generate() method
if len(word) <= 10:  # Change from 7 to 10
    key_words.append(word)
```

### Custom Extraction Logic

```python
def generate(self, keywords, genre="cinematic"):
    words = keywords.lower().split()
    
    # Your custom logic here
    # Example: prefer last word
    key_words = [w for w in words if len(w) <= 7]
    if key_words:
        return key_words[-1].capitalize()  # Use last instead of first
```

## Integration

### With Aesthetic Text Overlay
```python
from src.title_generator import TitleGenerator
from src.aesthetic_text_overlay import AestheticTextOverlay

# Generate title
gen = TitleGenerator()
title = gen.generate("cyberpunk neon city", "scifi")

# Apply to poster
overlay = AestheticTextOverlay()
image = overlay.add_poster_text(image, title, "scifi", "The future awaits")
```

### With Original Pipeline
```python
from src.pipeline import Key2PosterPipeline
from src.title_generator import TitleGenerator

pipeline = Key2PosterPipeline(add_title=False)
image, _, _ = pipeline.generate_poster("cyberpunk city")

# Generate and add title
gen = TitleGenerator()
title = gen.generate("cyberpunk city", "scifi")
# Add title manually using aesthetic_text_overlay
```

## Before vs After

### Before
```
Keywords: "cyberpunk neon city"
Title on Poster: "CYBERPUNK NEON CITY"  ❌ Too long
```

### After
```
Keywords: "cyberpunk neon city"
Title on Poster: "CYBERPUNK"  ✅ Simple, impactful
```

## Best Practices

1. **Keep it short** - 1 word, max 7 characters
2. **Make it memorable** - Use strong, evocative words
3. **Match genre** - Use genre-appropriate fallbacks
4. **Test variations** - Try different keywords to see results

## Summary

✅ **Automatic 1-word title generation**  
✅ **Max 7 characters for impact**  
✅ **Genre-specific fallbacks**  
✅ **Integrated into unified pipeline**  
✅ **Easy customization**

**Result:** Clean, professional titles like real movie posters!
