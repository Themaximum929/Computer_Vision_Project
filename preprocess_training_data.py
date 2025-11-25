"""Preprocess training data by removing text from posters"""
import argparse
from pathlib import Path
from PIL import Image
from src.aggressive_text_remover import AggressiveTextRemover
from tqdm import tqdm

def preprocess_posters(input_dir, output_dir, iterations=3):
    """Remove text from all posters in directory (preserves genre info)"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all image files
    image_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
    
    if not image_files:
        print(f"No images found in {input_dir}")
        return
    
    print(f"Found {len(image_files)} images to preprocess")
    print(f"Using aggressive text removal with {iterations} iterations")
    print(f"Preserving genre information from filenames")
    
    text_remover = AggressiveTextRemover()
    processed = 0
    genre_counts = {}
    
    for img_file in tqdm(image_files, desc="Preprocessing"):
        try:
            # Load image
            image = Image.open(img_file).convert("RGB")
            
            # Remove text
            cleaned_image, text_found = text_remover.remove_text(image, iterations=iterations)
            
            # Save to output directory (preserves original filename with genre)
            output_file = output_path / img_file.name
            cleaned_image.save(output_file, quality=95)
            processed += 1
            
            # Track genres from filename
            filename = img_file.stem
            if '_' in filename:
                genre_part = filename.split('_')[0]
                genre_counts[genre_part] = genre_counts.get(genre_part, 0) + 1
            
        except Exception as e:
            print(f"\nError processing {img_file.name}: {e}")
    
    # Copy metadata if exists
    metadata_file = input_path / "metadata.json"
    if metadata_file.exists():
        import shutil
        shutil.copy(metadata_file, output_path / "metadata.json")
        print(f"\n[OK] Copied metadata.json")
    
    print(f"\n[OK] Preprocessed {processed}/{len(image_files)} images")
    print(f"Output saved to: {output_dir}")
    
    if genre_counts:
        print(f"\nGenre distribution:")
        for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {genre}: {count} images")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess training data by removing text")
    parser.add_argument("--input", type=str, default="data/posters", help="Input directory with raw posters")
    parser.add_argument("--output", type=str, default="data/posters_clean", help="Output directory for cleaned posters")
    parser.add_argument("--iterations", type=int, default=3, help="Number of text removal iterations")
    args = parser.parse_args()
    
    preprocess_posters(args.input, args.output, args.iterations)
