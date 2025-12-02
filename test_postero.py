"""Test PosterO Integration"""
from src.pipeline import Key2PosterPipeline

# Test with PosterO layout generation
print("=" * 60)
print("Testing PosterO Integration (CVPR 2025)")
print("=" * 60)

pipeline = Key2PosterPipeline(
    use_flux=True,
    use_postero=True,  # Enable PosterO
    add_title=False,
    remove_text=True,
    aggressive_text_removal=True,
    poster_type='movie',
    style_preset='cinematic'
)

# Generate poster with PosterO layout
image, brief, metrics = pipeline.generate_poster(
    "cyberpunk neon city",
    output_path="outputs/postero_test.png",
    seed=42
)

print("\n" + "=" * 60)
print("PosterO Layout Generated Successfully!")
print("=" * 60)
print(f"Layout elements: {brief.get('template', {}).get('layers', [])}")
