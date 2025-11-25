"""Test Enhanced FLUX Text Generation"""
from src.enhanced_flux_text import EnhancedFluxText, StyleEnhancedFlux
from pathlib import Path

Path("outputs/flux_enhanced").mkdir(parents=True, exist_ok=True)

print("\n" + "="*60)
print("ENHANCED FLUX TEXT GENERATION")
print("="*60)

# Test 1: Basic enhancement (removes artifacts + clean title)
print("\n[1/3] Testing artifact removal + clean title overlay...")
generator = EnhancedFluxText()

test_cases = [
    ("cyberpunk neon city", "NEON CITY", "scifi"),
    ("dark horror mansion", "HORROR", "horror"),
    ("space adventure", "ADVENTURE", "action")
]

for i, (scene, title, genre) in enumerate(test_cases):
    print(f"  Generating: {scene}")
    image = generator.generate_with_clean_text(scene, title, genre, seed=42+i)
    image.save(f"outputs/flux_enhanced/clean_{i}_{genre}.png")
    print(f"  ✓ Saved: clean_{i}_{genre}.png")

# Test 2: Style presets
print("\n[2/3] Testing style presets...")
style_gen = StyleEnhancedFlux()

presets = ['cinematic', 'minimalist', 'neon', 'dark']
for i, preset in enumerate(presets):
    print(f"  Style: {preset}")
    image = style_gen.generate_poster(
        "cyberpunk city", 
        "CYBERPUNK", 
        "scifi", 
        seed=100+i, 
        style_preset=preset
    )
    image.save(f"outputs/flux_enhanced/style_{preset}.png")
    print(f"  ✓ Saved: style_{preset}.png")

# Test 3: Comparison (old vs new)
print("\n[3/3] Generating comparison...")
from src.flux_text_inpainting import FluxTextPrompt

old_gen = FluxTextPrompt()
old_image = old_gen.generate_with_text("cyberpunk neon city", "NEON CITY", "scifi", seed=42)
old_image.save("outputs/flux_enhanced/comparison_old.png")

new_image = generator.generate_with_clean_text("cyberpunk neon city", "NEON CITY", "scifi", seed=42)
new_image.save("outputs/flux_enhanced/comparison_new.png")

print("\n" + "="*60)
print("✅ DONE! Check outputs/flux_enhanced/")
print("\nEnhancements:")
print("  1. ✓ Artifact removal on generated images")
print("  2. ✓ Clean PIL title overlay (no artifacts)")
print("  3. ✓ Enhanced styling with presets")
print("  4. ✓ Vignette and contrast improvements")
print("="*60)
