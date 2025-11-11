"""Standalone script to remove text from existing poster images"""
import argparse
from pathlib import Path
from PIL import Image
from src.text_remover import TextRemover

def main():
    parser = argparse.ArgumentParser(description="Remove text from poster images")
    parser.add_argument("input", type=str, help="Input image path")
    parser.add_argument("--output", type=str, default=None, help="Output path (default: input_notxt.png)")
    args = parser.parse_args()
    
    # Load image
    if not Path(args.input).exists():
        print(f"Error: Image not found at {args.input}")
        return
    
    image = Image.open(args.input)
    print(f"Loaded image: {args.input} ({image.size[0]}x{image.size[1]})")
    
    # Remove text
    print("Detecting and removing text...")
    remover = TextRemover()
    cleaned, text_found = remover.remove_text(image)
    
    if text_found:
        print("✓ Text detected and removed")
    else:
        print("✓ No text detected")
    
    # Save result
    if args.output is None:
        input_path = Path(args.input)
        args.output = str(input_path.parent / f"{input_path.stem}_notxt{input_path.suffix}")
    
    cleaned.save(args.output, quality=95)
    print(f"✓ Saved to {args.output}")

if __name__ == "__main__":
    main()
