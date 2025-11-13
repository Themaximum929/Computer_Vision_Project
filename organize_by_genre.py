"""Organize training data by genre for separate LoRA training"""
import sys
import json
from pathlib import Path
import shutil
sys.path.append(str(Path(__file__).parent))

def organize_posters_by_genre(input_dir="data/posters", output_base="data/posters_by_genre"):
    """Organize posters into genre-specific folders"""
    input_path = Path(input_dir)
    output_base_path = Path(output_base)
    
    # Load metadata
    metadata_file = input_path / "metadata.json"
    if not metadata_file.exists():
        print("Error: metadata.json not found")
        return
    
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    # Genre mapping
    genre_map = {
        "action": ["action", "adventure", "war"],
        "scifi": ["sci-fi", "science fiction", "space"],
        "fantasy": ["fantasy", "animation"],
        "horror": ["horror", "thriller"],
        "romance": ["romance", "drama"],
        "comedy": ["comedy"]
    }
    
    # Create genre folders
    genre_data = {genre: [] for genre in genre_map.keys()}
    genre_data["general"] = []
    
    # Organize by genre
    for item in metadata:
        genres = [g.lower() for g in item.get("genres", [])]
        filename = Path(item["path"]).name
        
        # Find matching genre
        matched = False
        for target_genre, keywords in genre_map.items():
            if any(keyword in " ".join(genres) for keyword in keywords):
                genre_data[target_genre].append((filename, item))
                matched = True
                break
        
        if not matched:
            genre_data["general"].append((filename, item))
    
    # Copy files to genre folders
    for genre, items in genre_data.items():
        if len(items) == 0:
            continue
        
        genre_dir = output_base_path / genre
        genre_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy images
        for filename, item in items:
            src = input_path / filename
            dst = genre_dir / filename
            if src.exists():
                shutil.copy(src, dst)
        
        # Save genre-specific metadata
        genre_metadata = [item for _, item in items]
        with open(genre_dir / "metadata.json", "w") as f:
            json.dump(genre_metadata, f, indent=2)
        
        print(f"✓ {genre}: {len(items)} posters")
    
    print(f"\n✓ Organized into {output_base}")
    print("\nNext: Train genre-specific LoRAs:")
    for genre in genre_data.keys():
        if len(genre_data[genre]) > 0:
            print(f"  python src/train_lora.py --data-dir data/posters_by_genre/{genre} --output models/lora_{genre}")

if __name__ == "__main__":
    organize_posters_by_genre()
