"""Run poster generation pipeline with FLUX.1"""
import argparse
from src.concept_expander import ConceptExpander
from src.visual_generator_flux import VisualGeneratorFlux
from src.aggressive_text_remover import AggressiveTextRemover
from src.refiner import QualityRefiner
from src.text_overlay import TextOverlay
from src.genre_classifier import GenreClassifier
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Generate posters with FLUX.1")
    parser.add_argument("keywords", type=str, help="Keywords (2-5 words)")
    parser.add_argument("--model", default="black-forest-labs/FLUX.1-schnell", 
                       help="FLUX model (schnell or dev)")
    parser.add_argument("--steps", type=int, default=4, help="Inference steps")
    parser.add_argument("--add-title", action="store_true", help="Add styled title")
    parser.add_argument("--remove-text", action="store_true", help="Remove text")
    parser.add_argument("--enhance", action="store_true", help="Enhance quality")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--output", type=str, default=None, help="Output path")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("FLUX.1 POSTER GENERATION PIPELINE")
    print("="*60)
    
    # Step 1: Expand concept
    print("\n[1/5] Expanding concept...")
    expander = ConceptExpander()
    brief = expander.expand(args.keywords)
    print(f"    Mood: {brief['mood']}")
    print(f"    Sentiment: {brief['sentiment']}")
    
    # Step 2: Generate with FLUX.1
    print("\n[2/5] Generating with FLUX.1...")
    generator = VisualGeneratorFlux(model_id=args.model)
    image = generator.generate(
        prompt=brief['prompt'],
        num_inference_steps=args.steps,
        seed=args.seed
    )
    print("    ✓ Image generated")
    
    # Step 3: Remove text (optional)
    if args.remove_text:
        print("\n[3/5] Removing text...")
        remover = AggressiveTextRemover()
        image, _ = remover.remove_text(image)
        print("    ✓ Text removed")
    else:
        print("\n[3/5] Skipping text removal")
    
    # Step 4: Enhance (optional)
    if args.enhance:
        print("\n[4/5] Enhancing quality...")
        refiner = QualityRefiner()
        image = refiner.refine(image)
        print("    ✓ Quality enhanced")
    else:
        print("\n[4/5] Skipping enhancement")
    
    # Step 5: Add title (optional)
    if args.add_title:
        print("\n[5/5] Adding styled title...")
        classifier = GenreClassifier()
        genre = classifier.classify(args.keywords)
        
        overlay = TextOverlay()
        title = " ".join(args.keywords.split()[:3]).upper()
        image = overlay.add_title(image, title, genre=genre)
        print(f"    ✓ Title added (genre: {genre})")
    else:
        print("\n[5/5] Skipping title")
    
    # Save
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path("outputs/flux")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = args.keywords.replace(" ", "_")[:30] + ".png"
        output_path = output_dir / filename
    
    image.save(output_path)
    
    print("\n" + "="*60)
    print("✅ GENERATION COMPLETE!")
    print("="*60)
    print(f"\nSaved: {output_path}")
    print(f"Model: {args.model}")
    print(f"Steps: {args.steps}")

if __name__ == "__main__":
    main()
