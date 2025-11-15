"""Test baseline SD with ADVANCED ARTISTIC TEXT OVERLAY"""
from src.pipeline import Key2PosterPipeline

print("="*60)
print("TESTING: Advanced Artistic Text Overlay")
print("="*60)
print("Features:")
print("  - Genre-specific typography (7 unique styles)")
print("  - Multi-orientation text (rotated, angled, stacked)")
print("  - Artistic effects (shadows, glows, outlines, gradients)")
print("  - Font pairing (serif + sans-serif)")
print("  - Wide letter tracking for sci-fi")
print("  - Bounds-safe positioning")
print("="*60)

# Initialize pipeline with genre detection and text overlay
pipeline = Key2PosterPipeline(
    baseline_style=True,
    genre_lora=True,  # Enable genre detection for text styling
    add_title=True,   # Enable artistic text overlay
    remove_text=False,
    super_resolution=False
)

# Test cases with different genres
test_cases = [
    ("epic space battle", 42, "action"),
    ("dark horror mansion", 123, "horror"),
    ("romantic sunset beach", 456, "romance"),
    ("cyberpunk neon city", 789, "scifi"),
    ("fantasy dragon kingdom", 999, "fantasy")
]

for keywords, seed, expected_genre in test_cases:
    print(f"\n{'='*60}")
    print(f"Generating: '{keywords}' (Expected genre: {expected_genre})")
    print(f"{'='*60}")
    
    image, brief, metrics = pipeline.generate_poster(
        keywords,
        output_path=f"outputs/test_{keywords.replace(' ', '_')}.png",
        seed=seed,
        evaluate=True
    )
    
    print(f"\n✓ SAVED: outputs/test_{keywords.replace(' ', '_')}.png")
    print(f"  Aesthetic Score: {metrics['aesthetic']['overall']:.3f}")
    print(f"  Resolution: {metrics['resolution']['width']}x{metrics['resolution']['height']}")
    print(f"\n  Text Overlay Applied:")
    print(f"    - Genre-specific layout")
    print(f"    - Artistic typography")
    print(f"    - Multi-layer effects")
    print(f"    - Bounds-safe positioning")

print("\n" + "="*60)
print("TEST COMPLETE - CHECK RESULTS")
print("="*60)
print("\nCompare the outputs to see:")
print("  1. Different text layouts per genre")
print("  2. Rotated/angled text (action, thriller)")
print("  3. Glowing text (sci-fi, fantasy)")
print("  4. Stacked vs centered vs split layouts")
print("  5. Font pairing and varied typography")
print("  6. All text stays within poster boundaries")
print("\nOutputs saved in: outputs/")
