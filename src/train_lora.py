"""Script to train LoRA on scraped poster dataset"""
import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.lora_trainer import LoRATrainer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="data/posters", help="Training data directory")
    parser.add_argument("--output", type=str, default="models/poster_lora", help="Output directory")
    parser.add_argument("--epochs", type=int, default=20, help="Training epochs")
    args = parser.parse_args()
    
    data_dir = args.data_dir
    output_dir = args.output
    
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
        epochs=args.epochs,
        batch_size=1,
        lr=5e-5
    )
    
    print("\nTraining complete!")
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    main()
