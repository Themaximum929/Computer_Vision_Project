"""Scraper for product images (food, footwear, theme parks, etc.)"""
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
import time
from tqdm import tqdm
import json

class ProductScraper:
    def __init__(self, output_dir="data/products"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def scrape_unsplash(self, categories, images_per_category=20):
        """Scrape product images from Unsplash API"""
        # Unsplash API (free tier: 50 requests/hour)
        # Get your key from: https://unsplash.com/developers
        API_KEY = "YOUR_UNSPLASH_ACCESS_KEY"  # Replace with your key
        
        all_images = []
        metadata = []
        
        for category in categories:
            print(f"\nScraping {category} images...")
            
            url = f"https://api.unsplash.com/search/photos"
            params = {
                "query": category,
                "per_page": images_per_category,
                "orientation": "portrait",
                "client_id": API_KEY
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                for i, item in enumerate(tqdm(data.get('results', []), desc=f"{category}")):
                    try:
                        # Get image URL
                        img_url = item['urls']['regular']
                        img_id = item['id']
                        
                        # Download image
                        img_response = requests.get(img_url, timeout=10)
                        img = Image.open(BytesIO(img_response.content)).convert('RGB')
                        
                        # Resize to poster format
                        img = img.resize((720, 1280), Image.Resampling.LANCZOS)
                        
                        # Save with category prefix
                        save_path = self.output_dir / f"{category}_{img_id}.jpg"
                        img.save(save_path, quality=95)
                        
                        all_images.append(str(save_path))
                        metadata.append({
                            "id": img_id,
                            "category": category,
                            "path": str(save_path),
                            "source": "unsplash"
                        })
                        
                        time.sleep(0.5)  # Rate limiting
                    except Exception as e:
                        print(f"Error downloading {category} image: {e}")
                
            except Exception as e:
                print(f"Error scraping {category}: {e}")
        
        # Save metadata
        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n[OK] Scraped {len(all_images)} product images")
        return all_images, metadata
    
    def get_product_categories(self):
        """Get product categories for scraping"""
        return {
            "food": ["gourmet food", "restaurant dish", "food photography"],
            "footwear": ["sneakers", "shoes product", "footwear"],
            "theme_park": ["amusement park", "theme park", "roller coaster"],
            "fashion": ["fashion product", "clothing", "apparel"],
            "electronics": ["gadget", "tech product", "electronics"],
            "beverage": ["drink", "beverage", "cocktail"],
            "cosmetics": ["makeup", "cosmetics", "beauty product"],
            "travel": ["travel destination", "vacation", "tourism"]
        }

# Alternative: Use existing datasets
DATASET_SOURCES = """
Alternative Dataset Sources (No API key needed):

1. **Kaggle Datasets** (Free, high quality)
   - Food-101: https://www.kaggle.com/dansbecker/food-101
   - Shoe vs Sandal vs Boot: https://www.kaggle.com/datasets/hasibalmuzdadid/shoe-vs-sandal-vs-boot-dataset-15k-images
   - Fashion Product Images: https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset

2. **Hugging Face Datasets** (Free, easy to use)
   ```python
   from datasets import load_dataset
   
   # Food images
   dataset = load_dataset("food101")
   
   # Fashion images  
   dataset = load_dataset("ashraq/fashion-product-images-small")
   ```

3. **Google Open Images** (Free, massive)
   - Download tool: https://github.com/openimages/dataset
   - Categories: /m/02wbm (food), /m/0kpqd (footwear), etc.

4. **Pexels API** (Free, no rate limit)
   - API: https://www.pexels.com/api/
   - Similar to Unsplash but more generous limits

Usage:
1. Download dataset from Kaggle/HuggingFace
2. Extract to data/products/
3. Organize by category (food/, footwear/, etc.)
4. Run: python train_by_genre.py --data-dir data/products
"""

if __name__ == "__main__":
    print(DATASET_SOURCES)
