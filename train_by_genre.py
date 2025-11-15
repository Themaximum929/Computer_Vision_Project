"""Train genre-specific LoRA models from preprocessed data"""
import json
from pathlib import Path
from collections import defaultdict
from src.lora_trainer import LoRATrainer

def organize_by_genre(data_dir):
    """Organize posters by genre from metadata"""
    data_path = Path(data_dir)
    metadata_file = data_path / "metadata.json"
    
    if not metadata_file.exists():
        print("Error: metadata.json not found")
        print("Run download first: python download_product_data.py")
        return None
    
    # Load metadata
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    # Group by category
    genre_files = defaultdict(list)
    for item in metadata:
        category = item.get('category', item.get('genres', ['general'])[0])
        file_path = Path(item['path'])
        if file_path.exists():
            genre_files[category].append(str(file_path))
    
    return genre_files

def train_genre_loras(data_dir="data/posters_clean", output_base="models", min_images=10, epochs=20):
    """Train LoRA for each genre with sufficient data"""
    print("="*60)
    print("GENRE-SPECIFIC LORA TRAINING")
    print("="*60)
    
    # Organize by genre
    genre_files = organize_by_genre(data_dir)
    if not genre_files:
        return
    
    # Show genre distribution
    print("\nGenre distribution:")
    for genre, files in sorted(genre_files.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {genre}: {len(files)} images")
    
    # Train each genre with sufficient data
    print(f"\nTraining genres with >= {min_images} images...")
    trained = []
    
    for genre, files in genre_files.items():
        if len(files) < min_images:
            print(f"\n[SKIP] {genre}: Only {len(files)} images (need {min_images})")
            continue
        
        print(f"\n{'='*60}")
        print(f"Training {genre.upper()} LoRA ({len(files)} images)")
        print(f"{'='*60}")
        
        # Create temporary directory with genre images
        temp_dir = Path(f"data/temp_{genre}")
        temp_dir.mkdir(exist_ok=True)
        
        # Copy/link files
        import shutil
        for i, src_file in enumerate(files):
            dst_file = temp_dir / f"{genre}_{i}.jpg"
            shutil.copy(src_file, dst_file)
        
        # Train LoRA
        output_dir = f"{output_base}/lora_{genre}"
        trainer = LoRATrainer()
        
        try:
            trainer.train(
                data_dir=str(temp_dir),
                output_dir=output_dir,
                epochs=epochs,
                batch_size=1,
                lr=5e-5
            )
            trained.append(genre)
            print(f"\n[OK] {genre} LoRA saved to {output_dir}")
        except Exception as e:
            print(f"\n[ERROR] Failed to train {genre}: {e}")
        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"Trained {len(trained)} genre-specific LoRAs:")
    for genre in trained:
        print(f"  - {genre}: models/lora_{genre}/")
    print(f"\nUse with: python run_pipeline.py 'keywords' --genre-lora --add-title")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train genre-specific LoRA models")
    parser.add_argument("--data-dir", type=str, default="data/posters_clean", 
                        help="Directory with preprocessed posters")
    parser.add_argument("--output", type=str, default="models", 
                        help="Base output directory for LoRA models")
    parser.add_argument("--min-images", type=int, default=10, 
                        help="Minimum images required per genre")
    parser.add_argument("--epochs", type=int, default=20, 
                        help="Training epochs per genre")
    args = parser.parse_args()
    
    train_genre_loras(args.data_dir, args.output, args.min_images, args.epochs)
