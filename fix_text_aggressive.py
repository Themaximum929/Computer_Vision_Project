"""Aggressively remove text from existing poster"""
import argparse
from pathlib import Path
from PIL import Image
from src.aggressive_text_remover import AggressiveTextRemover

def main():
    parser = argparse.ArgumentParser(description="Aggressively remove text from poster")
    parser.add_argument("input", type=str, help="Input image path")
    parser.add_argument("--output", type=str, default=None, help="Output path")
    parser.add_argument("--iterations", type=int, default=3, help="Number of removal passes (default: 3)")
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: Image not found at {args.input}")
        return
    
    image = Image.open(args.input)
    print(f"Loaded: {args.input} ({image.size[0]}x{image.size[1]})")
    
    print(f"Aggressively removing text ({args.iterations} passes)...")
    remover = AggressiveTextRemover()
    cleaned, _ = remover.remove_text(image, iterations=args.iterations)
    
    if args.output is None:
        input_path = Path(args.input)
        args.output = str(input_path.parent / f"{input_path.stem}_clean{input_path.suffix}")
    
    cleaned.save(args.output, quality=95)
    print(f"✓ Saved to {args.output}")

if __name__ == "__main__":
    main()
