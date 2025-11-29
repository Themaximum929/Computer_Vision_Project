"""Demo: Hybrid Template System - Auto-Generated + Existing Templates"""
import sys
sys.path.insert(0, '.')

from src.pipeline import Key2PosterPipeline

print("=" * 70)
print("HYBRID TEMPLATE SYSTEM - Maximum Layout Diversity")
print("50% Auto-Generated + 50% Existing Templates")
print("=" * 70)

pipeline = Key2PosterPipeline(
    use_flux=True,
    remove_text=True,
    add_title=False,
    auto_template=True,  # Enables hybrid mode
    poster_type='movie'
)

keywords = "cyberpunk neon city"

print(f"\nGenerating 6 variations of: '{keywords}'")
print("=" * 70)

for i in range(6):
    print(f"\n[Variation {i+1}/6]")
    
    image, brief, metrics = pipeline.generate_poster(
        keywords,
        output_path=f"outputs/hybrid_variation_{i+1}.png",
        seed=42 + i
    )
    
    # Check if auto-generated or existing template
    if 'layout_type' in brief['template']:
        layout = brief['template']['layout_type']
        align = brief['template']['fonts']['title']['align']
        source = "AUTO-GENERATED"
    else:
        layout = "existing"
        align = "center"
        source = "EXISTING TEMPLATE"
    
    print(f"✅ Source: {source}")
    print(f"   Layout: {layout.upper()}")
    print(f"   Align: {align.upper()}")
    print(f"   Aesthetic: {metrics['aesthetic']['overall']:.3f}")

print("\n" + "=" * 70)
print("RESULT: Mix of algorithmic + handcrafted templates!")
print("Check outputs/hybrid_variation_*.png for diversity")
print("=" * 70)
