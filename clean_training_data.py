"""Clean training data by removing text from posters"""
from pathlib import Path
from PIL import Image
from src.aggressive_text_remover import AggressiveTextRemover
from tqdm import tqdm

def clean_posters(input_dir="data/posters", output_dir="data/posters_clean"):
    """Remove text from all training posters"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all images
    images = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
    
    if len(images) == 0:
        print(f"No images found in {input_dir}")
        return
    
    print(f"Cleaning {len(images)} posters...")
    print(f"Output: {output_dir}")
    
    remover = AggressiveTextRemover()
    
    for img_path in tqdm(images):
        try:
            # Skip metadata
            if img_path.name == "metadata.json":
                continue
            
            # Load image
            image = Image.open(img_path)
            
            # Remove text (5 passes for thorough cleaning)
            cleaned, _ = remover.remove_text(image, iterations=5)
            
            # Save cleaned image
            output_file = output_path / img_path.name
            cleaned.save(output_file, quality=95)
            
        except Exception as e:
            print(f"\nError processing {img_path.name}: {e}")
    
    # Copy metadata
    metadata_src = input_path / "metadata.json"
    if metadata_src.exists():
        import shutil
        shutil.copy(metadata_src, output_path / "metadata.json")
    
    print(f"\n✓ Cleaned {len(images)} posters")
    print(f"✓ Saved to {output_dir}")
    print("\nNext step: Train LoRA on cleaned data:")
    print(f"  python src/train_lora.py --data-dir {output_dir}")

if __name__ == "__main__":
    clean_posters()
