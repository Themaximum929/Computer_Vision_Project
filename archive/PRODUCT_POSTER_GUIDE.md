## New Approach: Product Poster Generator

### Why This Approach is Better

**Old Approach (Movie Posters):**
- ❌ Text removal has low success rate
- ❌ Movie posters have complex text overlays
- ❌ Preprocessing is cumbersome
- ❌ Hard to get clean training data

**New Approach (Product Posters):**
- ✅ Clean product images (no text to remove)
- ✅ Simple preprocessing (just resize)
- ✅ Focus on post-processing (composition + text)
- ✅ Easy to get training data (public datasets)
- ✅ More versatile (food, fashion, electronics, etc.)

---

## Complete Workflow

### Step 1: Download Product Images

**Option A: Hugging Face Datasets (Easiest)**
```bash
pip install datasets
python download_product_data.py --category all --count 50
```

**Option B: Kaggle Datasets (High Quality)**
1. Go to https://www.kaggle.com/datasets
2. Download:
   - Food-101: https://www.kaggle.com/dansbecker/food-101
   - Fashion Products: https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset
3. Extract to `data/products/food/` and `data/products/fashion/`

**Option C: Manual Collection**
- Download product images from Google Images
- Organize by category: `data/products/{category}/`
- Ensure images are clean (no text overlays)

---

### Step 2: Train Category-Specific LoRAs

```bash
python train_by_genre.py --data-dir data/products --min-images 20
```

This trains separate LoRAs for:
- `models/lora_food/`
- `models/lora_fashion/`
- `models/lora_electronics/`
- etc.

---

### Step 3: Generate Product Posters

```bash
# Food poster
python run_pipeline.py "delicious burger" --genre-lora --add-title

# Fashion poster
python run_pipeline.py "premium sneakers" --genre-lora --add-title

# Theme park poster
python run_pipeline.py "roller coaster adventure" --genre-lora --add-title
```

---

## Product Categories

| Category | Keywords | Style |
|----------|----------|-------|
| **Food** | burger, pizza, sushi, dessert | Orange-red, bold, appetizing |
| **Footwear** | sneakers, boots, shoes | White, clean, premium |
| **Theme Park** | roller coaster, adventure, fun | Gold/red, exciting, centered |
| **Fashion** | clothing, apparel, style | Black, elegant, luxury |
| **Electronics** | gadget, tech, innovation | Blue, modern, sleek |
| **Beverage** | drink, cocktail, refreshing | White/blue, cool, fresh |
| **Cosmetics** | makeup, beauty, skincare | Pink, soft, elegant |
| **Travel** | destination, vacation, explore | White/blue, adventurous |

---

## Data Sources

### 1. Hugging Face Datasets (Free, Easy)
```python
from datasets import load_dataset

# Food images
dataset = load_dataset("food101")

# Fashion images
dataset = load_dataset("ashraq/fashion-product-images-small")
```

### 2. Kaggle Datasets (Free, High Quality)
- Food-101: 101,000 food images
- Fashion Product Images: 44,000 fashion items
- Shoe Dataset: 15,000 footwear images

### 3. Unsplash API (Free, Beautiful)
- 50 requests/hour free tier
- High-quality product photography
- API key: https://unsplash.com/developers

### 4. Pexels API (Free, Generous)
- Unlimited requests
- Commercial use allowed
- API key: https://www.pexels.com/api/

---

## Advantages Over Movie Posters

### 1. **No Text Removal Needed**
Product images are clean - no preprocessing required!

### 2. **Better Training Data**
- Consistent lighting
- Clean backgrounds
- Professional photography
- Large public datasets

### 3. **More Versatile**
Can generate posters for:
- Restaurant menus
- Product advertisements
- Event promotions
- Social media marketing

### 4. **Easier Post-Processing**
Focus on:
- Text placement
- Color matching
- Brand styling
- Call-to-action text

---

## Example Outputs

### Food Poster
```
Input: "gourmet burger"
Output: 
- Image: Juicy burger with perfect lighting
- Title: "GOURMET BURGER" (orange-red, bold)
- Subtitle: "FRESH & DELICIOUS"
- Style: Appetizing, warm colors
```

### Fashion Poster
```
Input: "luxury sneakers"
Output:
- Image: Premium sneakers on clean background
- Title: "LUXURY SNEAKERS" (black, elegant)
- Subtitle: "PREMIUM COLLECTION"
- Style: Minimalist, sophisticated
```

### Theme Park Poster
```
Input: "roller coaster thrill"
Output:
- Image: Exciting roller coaster action
- Title: "ROLLER COASTER THRILL" (gold/red)
- Subtitle: "ADVENTURE AWAITS"
- Style: Energetic, centered, bold
```

---

## Quick Start

```bash
# 1. Download product images (50 per category)
python download_product_data.py --count 50

# 2. Train LoRAs
python train_by_genre.py --data-dir data/products

# 3. Generate poster
python run_pipeline.py "delicious pizza" --genre-lora --add-title

# 4. Launch web interface
python app_simple.py
```

---

## Comparison

| Aspect | Movie Posters | Product Posters |
|--------|---------------|-----------------|
| **Preprocessing** | Complex (text removal) | Simple (resize only) |
| **Text Removal Success** | ~30-40% | Not needed (100%) |
| **Training Data** | Hard to get clean | Easy (public datasets) |
| **Data Quality** | Variable | Consistent |
| **Post-Processing** | Simple | Advanced (composition) |
| **Use Cases** | Limited (movies) | Versatile (products) |
| **Commercial Value** | Low | High (marketing) |

---

## Implementation Changes

### What Stays the Same:
- ✅ Multi-agent architecture
- ✅ LoRA training pipeline
- ✅ Genre classification
- ✅ Text overlay system
- ✅ Quality evaluation

### What Changes:
- ❌ Remove: Text removal preprocessing
- ❌ Remove: Movie poster scraper
- ✅ Add: Product image downloader
- ✅ Add: Product text styles
- ✅ Add: Category-based training

---

## Next Steps

1. **Download Data**
   ```bash
   python download_product_data.py
   ```

2. **Train Models**
   ```bash
   python train_by_genre.py --data-dir data/products
   ```

3. **Generate Posters**
   ```bash
   python run_pipeline.py "your product" --genre-lora --add-title
   ```

4. **Customize Styles**
   Edit `src/product_text_styles.py` for your brand

---

## Summary

**Old:** Movie posters → Text removal (fails) → Train → Generate  
**New:** Product images (clean) → Train → Generate + Text overlay (works!)

**Result:** Higher quality, easier workflow, more versatile output! 🎨
