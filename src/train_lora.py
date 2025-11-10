"""Script to train LoRA on scraped poster dataset"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.lora_trainer import LoRATrainer

def main():
    data_dir = "data/posters"
    output_dir = "models/poster_lora"
    
    # Check if data exists
    if not Path(data_dir).exists() or len(list(Path(data_dir).glob("*.jpg"))) == 0:
        print(f"Error: No training data found in {data_dir}")
        print("Please run data collection first:")
        print("  python src/collect_data.py")
        sys.exit(1)
    
    print("Starting LoRA training...")
    print(f"Data directory: {data_dir}")
    print(f"Output directory: {output_dir}")
    
    trainer = LoRATrainer()
    trainer.train(
        data_dir=data_dir,
        output_dir=output_dir,
        epochs=10,
        batch_size=1,
        lr=1e-4
    )
    
    print("\nTraining complete!")
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    main()
