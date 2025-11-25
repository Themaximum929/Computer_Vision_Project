"""Enhanced FLUX Text Generation Test - Addresses 3 Issues"""
from src.pipeline import Key2PosterPipeline
from pathlib import Path

Path("outputs/flux_enhanced_comparison").mkdir(parents=True, exist_ok=True)

print("\n" + "="*70)
print("ENHANCED FLUX TEXT GENERATION - ISSUE FIXES")
print("="*70)
print("\nIssue 1: Artifacts on words in generated image (street banners, etc.)")
print("Issue 2: Added title should have no artifacts")
print("Issue 3: Enhanced styling of the poster")
print("="*70)

test_cases = [
    ("cyberpunk neon city", "scifi", "neon"),
    ("dark horror mansion", "horror", "dark"),
    ("space adventure", "action", "cinematic")
]

print("\n[OLD METHOD] - Original FLUX with potential artifacts")
print("-"*70)
pipeline_old = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=True,
    super_resolution=False,
    enhanced_flux=False
)
for i, (keywords, genre, style) in enumerate(test_cases):
    print(f"\n{i+1}. Generating: {keywords}")
    pipeline_old.generate_poster(
        keywords, 
        f"outputs/flux_enhanced_comparison/old_{i}_{genre}.png",
        seed=42+i,
        evaluate=False
    )
    print(f"   ✓ Saved: old_{i}_{genre}.png")

print("\n" + "="*70)
print("[NEW METHOD] - Enhanced FLUX with fixes")
print("-"*70)
pipeline_new = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=True,
    super_resolution=False,
    enhanced_flux=True
)
for i, (keywords, genre, style) in enumerate(test_cases):
    print(f"\n{i+1}. Generating: {keywords}")
    print(f"   Style preset: {style}")
    pipeline_new.style_preset = style
    pipeline_new.generate_poster(
        keywords,
        f"outputs/flux_enhanced_comparison/new_{i}_{genre}.png",
        seed=42+i,
        evaluate=False
    )
    print(f"   ✓ Saved: new_{i}_{genre}.png")

print("\n" + "="*70)
print("✅ COMPARISON COMPLETE!")
print("="*70)
print("\nCheck: outputs/flux_enhanced_comparison/")
print("\nEnhancements Applied:")
print("  1. ✓ Artifact removal - Blurs text artifacts in generated images")
print("  2. ✓ Clean title overlay - PIL-based text with no artifacts")
print("  3. ✓ Enhanced styling - Vignette, contrast boost, style presets")
print("\nStyle Presets Available:")
print("  - cinematic: Dramatic lighting, high contrast")
print("  - minimalist: Clean composition, negative space")
print("  - neon: Vibrant neon colors, cyberpunk aesthetic")
print("  - dark: Dark moody atmosphere, noir style")
print("  - vintage: Retro poster style, grain texture")
print("="*70)
