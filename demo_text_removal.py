"""Demo: Compare poster generation with and without text removal"""
from src.pipeline import Key2PosterPipeline

def main():
    print("="*60)
    print("TEXT REMOVAL DEMO")
    print("="*60)
    
    keywords = "space exploration adventure"
    seed = 42
    
    # Generate with text removal (default)
    print("\n[1/2] Generating with text removal...")
    pipeline_with = Key2PosterPipeline(use_lora=True, remove_text=True)
    image_with, _, _ = pipeline_with.generate_poster(
        keywords, 
        output_path="outputs/demo_with_text_removal.png",
        seed=seed
    )
    
    # Generate without text removal
    print("\n[2/2] Generating without text removal...")
    pipeline_without = Key2PosterPipeline(use_lora=True, remove_text=False)
    image_without, _, _ = pipeline_without.generate_poster(
        keywords,
        output_path="outputs/demo_without_text_removal.png", 
        seed=seed
    )
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nCompare the results:")
    print("  With text removal:    outputs/demo_with_text_removal.png")
    print("  Without text removal: outputs/demo_without_text_removal.png")

if __name__ == "__main__":
    main()
