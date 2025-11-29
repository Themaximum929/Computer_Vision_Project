"""Example: CLG-LO Layout Generation"""
from src.smart_compositor import SmartCompositor
from src.pipeline import Key2PosterPipeline
from PIL import Image

def example_clg_lo():
    """Demonstrate CLG-LO layout generation"""
    
    # Initialize pipeline
    print("Initializing CLG-LO pipeline...")
    pipeline = Key2PosterPipeline(use_flux=True, remove_text=True, add_title=False)
    compositor = SmartCompositor(use_clg_lo=True)
    
    # Test cases
    test_cases = [
        ("anime love story japanese", 42),
        ("cyberpunk neon city", 123),
        ("summer beach party", 456)
    ]
    
    for keywords, seed in test_cases:
        print(f"\n{'='*60}")
        print(f"Generating: {keywords} (seed={seed})")
        print(f"{'='*60}")
        
        # Step 1: Expand concepts
        print("\n[1/3] Expanding concepts...")
        brief = pipeline.expander.expand(keywords)
        title = brief.get('story title', brief.get('title', keywords.title()))
        captions = brief.get('captions', [])
        print(f"  Title: {title}")
        print(f"  Captions: {captions}")
        
        # Step 2: Generate FLUX image
        print("\n[2/3] Generating FLUX image (1920x1080)...")
        flux_img = pipeline.generator.generate(
            f"{brief['description']}, no text, no words",
            seed=seed,
            width=1920,
            height=1080
        )
        print(f"  ✓ Generated {flux_img.size}")
        
        # Step 3: Compose with CLG-LO
        print("\n[3/3] Composing with CLG-LO layout...")
        poster, metadata = compositor.compose_poster(
            flux_img,
            title,
            captions,
            keywords,
            seed
        )
        
        # Display results
        print(f"\n✅ Poster generated!")
        print(f"  Background: {metadata['bg_color']}")
        print(f"  Composition offset: {metadata['composition_offset']}")
        print(f"  Text elements: {len(metadata['text_layouts'])}")
        
        for i, layout in enumerate(metadata['text_layouts']):
            print(f"    {i+1}. '{layout['text']}' at ({layout['x']}, {layout['y']})")
            print(f"       Size: {layout['size']}px, Align: {layout['align']}")
        
        # Save
        output_path = f"outputs/clg_lo_{keywords.replace(' ', '_')}.png"
        poster.save(output_path)
        print(f"\n💾 Saved to: {output_path}")

def compare_modes():
    """Compare CLG-LO vs Rule-based"""
    print("\n" + "="*60)
    print("COMPARISON: CLG-LO vs Rule-based")
    print("="*60)
    
    pipeline = Key2PosterPipeline(use_flux=True, remove_text=True, add_title=False)
    keywords = "cyberpunk neon city"
    seed = 42
    
    # Generate FLUX image once
    brief = pipeline.expander.expand(keywords)
    title = brief.get('story title', brief.get('title', keywords.title()))
    captions = brief.get('captions', [])
    flux_img = pipeline.generator.generate(
        f"{brief['description']}, no text",
        seed=seed, width=1920, height=1080
    )
    
    # CLG-LO mode
    print("\n[CLG-LO Mode]")
    compositor_clg = SmartCompositor(use_clg_lo=True)
    poster_clg, meta_clg = compositor_clg.compose_poster(
        flux_img, title, captions, keywords, seed
    )
    poster_clg.save("outputs/compare_clg_lo.png")
    print(f"  Text elements: {len(meta_clg['text_layouts'])}")
    print(f"  Constraints: Overlap, Alignment, Hierarchy, Border, Balance")
    
    # Rule-based mode
    print("\n[Rule-based Mode]")
    compositor_rule = SmartCompositor(use_clg_lo=False)
    poster_rule, meta_rule = compositor_rule.compose_poster(
        flux_img, title, captions, keywords, seed
    )
    poster_rule.save("outputs/compare_rule_based.png")
    print(f"  Text elements: {len(meta_rule['text_layouts'])}")
    print(f"  Constraints: Border, Empty regions")
    
    print("\n✅ Comparison complete!")
    print("  CLG-LO: outputs/compare_clg_lo.png")
    print("  Rule-based: outputs/compare_rule_based.png")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        compare_modes()
    else:
        example_clg_lo()
    
    print("\n" + "="*60)
    print("Done! Check outputs/ folder for results.")
    print("="*60)
