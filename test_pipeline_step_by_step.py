"""Test pipeline step by step"""

print("="*60)
print("MOVIE POSTER PIPELINE TEST")
print("="*60)

# Step 1: Check data
print("\n[Step 1] Checking data...")
from pathlib import Path
import json

metadata_file = Path("data/posters/metadata.json")
if metadata_file.exists():
    with open(metadata_file) as f:
        metadata = json.load(f)
    print(f"  [OK] Found {len(metadata)} posters")
    
    # Count by genre
    genres = {}
    for item in metadata:
        for genre in item.get('genres', ['unknown']):
            genres[genre] = genres.get(genre, 0) + 1
    
    print(f"  [OK] Genres: {len(genres)}")
    for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"       {genre}: {count}")
else:
    print("  [ERROR] metadata.json not found")
    exit(1)

# Step 2: Test imports
print("\n[Step 2] Testing imports...")
try:
    from src.pipeline import Key2PosterPipeline
    print("  [OK] Pipeline imported")
except Exception as e:
    print(f"  [ERROR] {e}")
    exit(1)

# Step 3: Test baseline generation
print("\n[Step 3] Testing baseline generation...")
try:
    pipeline = Key2PosterPipeline(
        baseline_style=True,
        add_title=False,
        remove_text=False,
        super_resolution=False
    )
    print("  [OK] Pipeline initialized")
    
    print("  Generating test poster (this takes ~2 min on CPU)...")
    image, brief, metrics = pipeline.generate_poster(
        "epic battle",
        output_path="outputs/test_baseline.png",
        seed=42,
        evaluate=True
    )
    print(f"  [OK] Generated: outputs/test_baseline.png")
    print(f"       Resolution: {metrics['resolution']['width']}x{metrics['resolution']['height']}")
    
except Exception as e:
    print(f"  [ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nNext steps:")
print("1. Check outputs/test_baseline.png")
print("2. If good, train LoRA: python train_by_genre.py --data-dir data/posters")
print("3. Generate with LoRA: python run_pipeline.py 'space adventure' --genre-lora --add-title")
