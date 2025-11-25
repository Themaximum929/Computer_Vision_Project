"""Test FLUX generating text directly in image"""
from src.flux_text_inpainting import FluxTextPrompt
from pathlib import Path

Path("outputs/flux_text_test").mkdir(parents=True, exist_ok=True)

print("\n" + "="*60)
print("FLUX TEXT GENERATION TEST")
print("Testing FLUX's ability to generate text in images")
print("="*60)

generator = FluxTextPrompt()

test_cases = [
    ("cyberpunk neon city", "NEON CITY", "scifi"),
    ("dark horror mansion", "HORROR", "horror"),
    ("space adventure", "ADVENTURE", "action")
]

for i, (scene, title, genre) in enumerate(test_cases):
    print(f"\n[{i+1}/3] Generating: {scene} with title '{title}'")
    print("-"*60)
    
    image = generator.generate_with_text(
        base_prompt=scene,
        title=title,
        genre=genre,
        seed=42+i
    )
    
    output = f"outputs/flux_text_test/flux_gen_{i}_{title.lower()}.png"
    image.save(output)
    print(f"✓ Saved: {output}")

print("\n" + "="*60)
print("✅ DONE! Check outputs/flux_text_test/")
print("\nNote: FLUX text generation is unreliable.")
print("Text may be:")
print("  - Misspelled")
print("  - Wrong style")
print("  - Missing entirely")
print("  - In wrong position")
print("\nThis is why PIL overlay is preferred.")
print("="*60)
