# How to Get Real Product Poster Images

## The Problem
Fashion/clothing datasets show **models wearing clothes**, not **product posters**.

## Solution: Use These Sources

### Option 1: Google Images (Easiest, Manual)

**Search Terms:**
- "food poster design"
- "restaurant poster"
- "product advertisement poster"
- "sneaker advertisement"
- "theme park poster"

**Steps:**
1. Google Image Search with terms above
2. Filter: Size > Large
3. Download 20-50 images per category
4. Save to `data/products/{category}/`
5. Create metadata manually (see below)

---

### Option 2: Pinterest (High Quality)

**Search:**
- "food poster design"
- "product poster"
- "advertisement poster"

**Advantage:** Actual poster designs, not just product photos

---

### Option 3: Behance/Dribbble (Professional)

**URLs:**
- https://www.behance.net/search/projects?search=food+poster
- https://dribbble.com/search/food-poster

**Advantage:** Professional poster designs

---

### Option 4: Unsplash with Specific Queries

```python
# Use these search terms for poster-style images
queries = {
    "food": "food advertisement poster",
    "fashion": "sneaker product shot white background",
    "electronics": "gadget product photography",
    "beverage": "drink advertisement"
}
```

---

### Option 5: Use Existing Poster Datasets

**Kaggle:**
- Search: "advertisement poster"
- Search: "product poster"
- Search: "marketing poster"

---

## Quick Manual Setup

### Step 1: Create Directory Structure
```bash
mkdir -p data/products/food
mkdir -p data/products/fashion
mkdir -p data/products/electronics
```

### Step 2: Download Images
- Google "food poster design"
- Save 20-50 images to `data/products/food/`
- Rename: `food_001.jpg`, `food_002.jpg`, etc.

### Step 3: Create Metadata
```bash
python create_metadata.py --data-dir data/products
```

---

## Recommended Approach

### For Food Posters:
**Google Search:** "restaurant poster design"
- McDonald's posters
- Burger King posters
- Pizza Hut posters
- Food delivery app posters

### For Fashion/Footwear:
**Google Search:** "sneaker advertisement poster"
- Nike posters
- Adidas posters
- Product launch posters

### For Electronics:
**Google Search:** "tech product poster"
- Apple product posters
- Samsung posters
- Gadget launch posters

### For Theme Parks:
**Google Search:** "theme park poster"
- Disney posters
- Universal Studios posters
- Six Flags posters

---

## Alternative: Use SD to Generate Training Data

Since you have Stable Diffusion, you can **generate your own training data**:

```bash
# Generate food posters
python generate_training_data.py --category food --count 50

# Generate fashion posters
python generate_training_data.py --category fashion --count 50
```

This creates clean, poster-style images without needing to scrape!

---

## Best Practice

**Mix of sources:**
1. 20 images from Google (real posters)
2. 20 images from Pinterest (designs)
3. 10 images from Unsplash (product photos)

**Total:** 50 images per category = Good LoRA training

---

## Quick Start (Manual Method)

```bash
# 1. Download images manually
# Google: "food poster design" → Save 30 images to data/products/food/

# 2. Create metadata
python create_metadata.py --data-dir data/products

# 3. Train
python train_by_genre.py --data-dir data/products

# 4. Generate
python run_pipeline.py "delicious burger" --genre-lora --add-title
```

---

## Summary

**Don't use:** Generic product photos (models, plain backgrounds)  
**Do use:** Actual poster designs (text layouts, compositions, marketing style)

**Best sources:**
1. Google Images: "product poster design"
2. Pinterest: Professional poster designs
3. Behance: High-quality marketing posters

**Result:** Train on real posters → Generate real poster-style outputs!
