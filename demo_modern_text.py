"""Demo: Modern FLUX-based text rendering"""
from src.pipeline import Key2PosterPipeline
from pathlib import Path

Path("outputs/demo").mkdir(parents=True, exist_ok=True)

print("\n" + "="*60)
print("MODERN TEXT RENDERING DEMO")
print("="*60)

# Create pipeline with modern text enabled
pipeline = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=True,
    modern_text=True,  # ← Enable modern FLUX text rendering
    super_resolution=False
)

# Test different genres
test_cases = [
    ("cyberpunk neon city", "scifi"),
    ("dark horror mansion", "horror"),
    ("space adventure epic", "action")
]

for i, (keywords, expected_genre) in enumerate(test_cases):
    print(f"\n[{i+1}/3] Generating: {keywords}")
    print("-"*60)
    
    output = f"outputs/demo/modern_{i}_{keywords.replace(' ', '_')}.png"
    pipeline.generate_poster(keywords, output, seed=42+i)
    
    print(f"✓ Saved: {output}")

print("\n" + "="*60)
print("✅ DONE! Check outputs/demo/ for results")
print("="*60)
print("\nModern text features:")
print("  ✓ Text generated with FLUX diffusion")
print("  ✓ Natural integration with poster")
print("  ✓ Genre-aware styling")
print("  ✓ Professional typography")
