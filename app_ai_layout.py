"""Demo: Automatic Template Generation (Level 3 Innovation)"""
import sys
sys.path.insert(0, '.')

from src.pipeline import Key2PosterPipeline

print("=" * 60)
print("AUTOMATIC TEMPLATE GENERATION - Level 3 Innovation")
print("=" * 60)

# Initialize with auto-template generation
pipeline = Key2PosterPipeline(
    use_flux=True,
    remove_text=True,
    add_title=False,
    auto_template=True,  # Enable automatic template generation
    poster_type='movie'
)

# Generate posters with AI-generated layouts
test_cases = [
    ("anime love story japanese", "movie"),
    ("rock concert festival", "music"),
    ("summer sale event", "event"),
    ("basketball championship", "sports")
]

for keywords, genre in test_cases:
    print(f"\n{'='*60}")
    print(f"Generating: {keywords} ({genre})")
    print(f"{'='*60}")
    
    pipeline.poster_type = genre
    image, brief, metrics = pipeline.generate_poster(
        keywords,
        output_path=f"outputs/auto_{genre}_{keywords.replace(' ', '_')}.png",
        seed=42
    )
    
    print(f"\n✅ Generated with auto-template:")
    print(f"   Layout: {brief['template'].get('layout_type', 'standard')}")
    print(f"   Size: {brief['template']['size']}")
    print(f"   Aesthetic: {metrics['aesthetic']['overall']:.3f}")

print(f"\n{'='*60}")
print("COMPARISON: Static vs Auto-Generated Templates")
print(f"{'='*60}")
