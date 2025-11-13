"""Train separate LoRAs for each genre"""
import sys
from pathlib import Path
import subprocess
sys.path.append(str(Path(__file__).parent))

def train_all_genres():
    """Train LoRA for each genre"""
    base_dir = Path("data/posters_by_genre")
    
    if not base_dir.exists():
        print("Error: Genre-organized data not found")
        print("Run: python organize_by_genre.py")
        return
    
    genres = [d.name for d in base_dir.iterdir() if d.is_dir()]
    
    print(f"Found {len(genres)} genres: {', '.join(genres)}")
    print("\nTraining LoRAs for each genre...")
    print("This will take 10-30 minutes per genre\n")
    
    for i, genre in enumerate(genres):
        genre_dir = base_dir / genre
        output_dir = f"models/lora_{genre}"
        
        # Check if enough data
        images = list(genre_dir.glob("*.jpg")) + list(genre_dir.glob("*.png"))
        if len(images) < 5:
            print(f"[{i+1}/{len(genres)}] Skipping {genre} (only {len(images)} images)")
            continue
        
        print(f"[{i+1}/{len(genres)}] Training {genre} LoRA ({len(images)} images)...")
        
        # Train using same Python interpreter
        cmd = [
            sys.executable, "src/train_lora.py",
            "--data-dir", str(genre_dir),
            "--output", output_dir,
            "--epochs", "20"
        ]
        
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print(f"  ✓ {genre} LoRA trained successfully\n")
        else:
            print(f"  ✗ {genre} LoRA training failed\n")
    
    print("\n✓ All genre LoRAs trained!")
    print("\nTrained models:")
    for genre in genres:
        model_path = Path(f"models/lora_{genre}")
        if model_path.exists():
            print(f"  - {genre}: models/lora_{genre}")
    
    print("\nUsage:")
    print("  python app.py")
    print("  Enable 'Genre-Based LoRA' option")

if __name__ == "__main__":
    train_all_genres()
