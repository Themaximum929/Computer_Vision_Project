"""Create metadata.json for manually collected product images"""
from pathlib import Path
import json

def create_metadata(data_dir="data/products"):
    """Scan directories and create metadata.json"""
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Error: {data_dir} does not exist")
        print("Create it with: mkdir -p data/products/food data/products/fashion")
        return
    
    all_metadata = []
    categories = {}
    
    # Scan subdirectories
    for category_dir in data_path.iterdir():
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        image_files = list(category_dir.glob("*.jpg")) + list(category_dir.glob("*.png"))
        
        if not image_files:
            continue
        
        categories[category] = len(image_files)
        
        for img_file in image_files:
            all_metadata.append({
                "id": img_file.stem,
                "category": category,
                "path": str(img_file),
                "source": "manual"
            })
    
    if not all_metadata:
        print("No images found!")
        print("\nExpected structure:")
        print("  data/products/")
        print("    food/")
        print("      food_001.jpg")
        print("      food_002.jpg")
        print("    fashion/")
        print("      fashion_001.jpg")
        return
    
    # Save metadata
    metadata_file = data_path / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(all_metadata, f, indent=2)
    
    print(f"[OK] Created metadata for {len(all_metadata)} images")
    print(f"\nCategory distribution:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} images")
    
    print(f"\nSaved to: {metadata_file}")
    print(f"\nNext step:")
    print(f"  python train_by_genre.py --data-dir {data_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create metadata for manual images")
    parser.add_argument("--data-dir", type=str, default="data/products",
                        help="Directory containing category subdirectories")
    args = parser.parse_args()
    
    create_metadata(args.data_dir)
