"""Complete Key2Poster Pipeline Runner"""
import argparse
from pathlib import Path
from src.pipeline import Key2PosterPipeline

def main():
    parser = argparse.ArgumentParser(description="Key2Poster: Generate posters from keywords")
    parser.add_argument("keywords", type=str, help="2-5 keywords for poster generation")
    parser.add_argument("--output", type=str, default="outputs/poster.png", help="Output path")
    parser.add_argument("--lora", action="store_true", help="Use LoRA fine-tuned model")
    parser.add_argument("--lora-path", type=str, default="models/poster_lora", help="Path to LoRA weights")
    parser.add_argument("--genre-lora", action="store_true", help="Auto-detect genre and use genre-specific LoRA")
    parser.add_argument("--baseline-style", action="store_true", help="Use baseline SD without LoRA")
    parser.add_argument("--add-title", action="store_true", help="Add styled title overlay")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--no-text-removal", action="store_true", help="Disable text removal")
    parser.add_argument("--aggressive-text-removal", action="store_true", help="Use aggressive text removal")
    parser.add_argument("--no-super-res", action="store_true", help="Disable super-resolution enhancement")
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = Key2PosterPipeline(
        lora_path=args.lora_path if args.lora else None,
        use_lora=args.lora,
        genre_lora=args.genre_lora,
        baseline_style=args.baseline_style,
        add_title=args.add_title,
        remove_text=not args.no_text_removal,
        aggressive_text_removal=args.aggressive_text_removal,
        super_resolution=not args.no_super_res
    )
    
    # Generate poster
    image, brief, metrics = pipeline.generate_poster(
        args.keywords,
        output_path=args.output,
        seed=args.seed
    )
    
    print(f"\n✓ Success! Poster saved to {args.output}")

if __name__ == "__main__":
    main()
