"""Download product images from Hugging Face datasets (no API key needed)"""
from pathlib import Path
from PIL import Image
import json
from tqdm import tqdm

def download_food_images(output_dir="data/products/food", max_images=50):
    """Download food images from Food-101 dataset"""
    try:
        from datasets import load_dataset
    except ImportError:
        print("Installing datasets library...")
        import subprocess
        subprocess.check_call(["pip", "install", "datasets"])
        from datasets import load_dataset
    
    print("Downloading Food-101 dataset...")
    dataset = load_dataset("food101", split="train", streaming=True)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    metadata = []
    count = 0
    
    for item in tqdm(dataset, total=max_images, desc="Food images"):
        if count >= max_images:
            break
        
        try:
            img = item['image'].convert('RGB')
            img = img.resize((720, 1280), Image.Resampling.LANCZOS)
            
            save_path = output_path / f"food_{count:04d}.jpg"
            img.save(save_path, quality=95)
            
            metadata.append({
                "id": f"food_{count:04d}",
                "category": "food",
                "label": item.get('label', 'unknown'),
                "path": str(save_path)
            })
            count += 1
        except Exception as e:
            print(f"Error: {e}")
    
    with open(output_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n[OK] Downloaded {count} food images to {output_dir}")

def download_fashion_images(output_dir="data/products/fashion", max_images=50):
    """Download fashion/footwear images"""
    try:
        from datasets import load_dataset
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "datasets"])
        from datasets import load_dataset
    
    print("Downloading Fashion dataset...")
    dataset = load_dataset("ashraq/fashion-product-images-small", split="train", streaming=True)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    metadata = []
    count = 0
    
    for item in tqdm(dataset, total=max_images, desc="Fashion images"):
        if count >= max_images:
            break
        
        try:
            img = item['image'].convert('RGB')
            img = img.resize((720, 1280), Image.Resampling.LANCZOS)
            
            save_path = output_path / f"fashion_{count:04d}.jpg"
            img.save(save_path, quality=95)
            
            metadata.append({
                "id": f"fashion_{count:04d}",
                "category": "fashion",
                "path": str(save_path)
            })
            count += 1
        except Exception as e:
            print(f"Error: {e}")
    
    with open(output_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n[OK] Downloaded {count} fashion images to {output_dir}")

def download_all_categories(images_per_category=50):
    """Download images for all product categories"""
    print("="*60)
    print("PRODUCT IMAGE DOWNLOAD")
    print("="*60)
    
    all_metadata = []
    
    categories = {
        "food": download_food_images,
        "fashion": download_fashion_images,
    }
    
    for category, download_func in categories.items():
        print(f"\n--- {category.upper()} ---")
        try:
            download_func(f"data/products/{category}", images_per_category)
            # Load category metadata
            meta_file = Path(f"data/products/{category}/metadata.json")
            if meta_file.exists():
                with open(meta_file) as f:
                    cat_meta = json.load(f)
                    all_metadata.extend(cat_meta)
        except Exception as e:
            print(f"Failed to download {category}: {e}")
    
    # Save consolidated metadata
    if all_metadata:
        with open("data/products/metadata.json", "w") as f:
            json.dump(all_metadata, f, indent=2)
        print(f"\n[OK] Saved consolidated metadata: {len(all_metadata)} images")
    
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Train LoRA: python train_by_genre.py --data-dir data/products")
    print("2. Generate: python run_pipeline.py 'delicious burger' --genre-lora --add-title")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download product images")
    parser.add_argument("--category", type=str, choices=["food", "fashion", "all"], 
                        default="all", help="Category to download")
    parser.add_argument("--count", type=int, default=50, 
                        help="Images per category")
    args = parser.parse_args()
    
    if args.category == "all":
        download_all_categories(args.count)
    elif args.category == "food":
        download_food_images(max_images=args.count)
    elif args.category == "fashion":
        download_fashion_images(max_images=args.count)
