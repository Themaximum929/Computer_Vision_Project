# Pipeline Modifications Summary

## New Workflow (5 Steps)

### 1. User Prompt Submission
- User enters 2-5 keywords
- Validates input

### 2. Random Template Selection
- Automatically selects a random poster template from `templates/` folder
- Extracts image region dimensions from template
- Template defines:
  - Poster size (e.g., 720x1080)
  - Image placement bbox
  - Text placement bbox
  - Background layer

### 3. Prompt Enhancement (TODO)
- **Current:** Basic concept expansion with sentiment analysis
- **TODO:** Advanced prompt enhancement (teammates will implement)
- Passes image size from template to enhancement module
- Enhanced prompt includes:
  - Sentiment analysis
  - Mood detection
  - Thematic expansion
  - Image dimensions for optimal generation

### 4. FLUX Image Generation
- Generates image using FLUX.1-schnell
- Uses enhanced prompt from step 3
- Automatically resizes to fit template's image region
- No text in generated image (clean visual)

### 5. Template Composition
- Merges FLUX-generated image with template
- Places image in designated bbox from template
- Adds LLM-processed text overlay
  - Text: Title derived from keywords
  - Position: From template text layer
  - Font: Graduate-Regular, 37px
  - Color: Blue (#043bb4)
- Creates final poster with:
  - Background layer (template color)
  - Generated image (FLUX)
  - Text overlay (LLM processed)

## Key Changes

### `src/pipeline.py`
- Added `template` parameter to `generate_poster()`
- Step 1: Random template selection
- Step 2: Prompt enhancement with image size (TODO marker for teammates)
- Step 4: FLUX generation with automatic resizing
- Step 5: Template composition with image merging and text overlay
- Returns template info in `brief` dictionary

### `app.py`
- Added progress indicators for each step
- Updated info display to show template-based composition
- Added TODO comment for prompt enhancement

## Data Flow

```
User Keywords
    ↓
[1] Random Template Selection
    ↓ (template + image_size)
[2] Prompt Enhancement (TODO: teammates)
    ↓ (enhanced_prompt + image_size)
[3] FLUX Generation
    ↓ (raw_image)
[4] Resize to Template
    ↓ (resized_image)
[5] Compose Final Poster
    ↓ (template + image + text)
Final Poster
```

## Template Structure

Templates are JSON files with:
```json
{
  "size": [720, 1080],
  "layers": [
    {
      "name": "Background",
      "bbox": [0, 0, 720, 1080]
    },
    {
      "name": "Image",
      "bbox": [54, 59, 655, 873]
    },
    {
      "name": "Text",
      "bbox": [240, 930, 472, 989]
    }
  ]
}
```

## TODO for Teammates

In `src/pipeline.py`, Step 2 (line ~95):
```python
# Step 2: Expand concepts (TODO: Enhancement by teammates)
print(f"\n[2/5] Expanding concepts for: '{keywords}'")
brief = self.expander.expand(keywords)
print(f"  TODO: Advanced prompt enhancement (teammates will implement)")
```

**What to implement:**
- Advanced prompt enhancement module
- Use `image_size` variable for context
- Enhance `brief['prompt']` with better descriptions
- Consider template layout in enhancement
- Return enhanced prompt that works well with FLUX

## Testing

```bash
# Test the new pipeline
python app.py

# Or test directly
python -c "
from src.pipeline import Key2PosterPipeline
pipeline = Key2PosterPipeline(use_flux=True, add_title=False, genre_lora=False)
image, brief, metrics = pipeline.generate_poster('cyberpunk neon city')
print('Template used:', brief.get('template', {}).get('size'))
"
```

## Benefits

1. ✅ **Consistent Layout** - Templates ensure professional composition
2. ✅ **Random Variety** - Different templates for each generation
3. ✅ **Proper Sizing** - FLUX generates images that fit template regions
4. ✅ **Clean Separation** - Image generation separate from text overlay
5. ✅ **Extensible** - Easy for teammates to enhance prompt module
6. ✅ **LLM Integration** - Text processing separate from image generation
