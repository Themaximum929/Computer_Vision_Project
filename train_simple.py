"""Simple LoRA training on movie posters"""
from pathlib import Path
from src.lora_trainer import LoRATrainer

print("="*60)
print("TRAINING LORA ON MOVIE POSTERS")
print("="*60)

# Check data
data_dir = Path("data/posters")
images = list(data_dir.glob("*.jpg"))

if len(images) < 20:
    print(f"Error: Only {len(images)} images found. Need at least 20.")
    exit(1)

print(f"\nFound {len(images)} movie posters")
print("Training LoRA (this will take 10-20 minutes)...")
print("Note: Training on posters WITH text is OK - negative prompt will handle it\n")

# Train
trainer = LoRATrainer()
trainer.train(
    data_dir=str(data_dir),
    output_dir="models/movie_lora",
    epochs=15,
    batch_size=1,
    lr=5e-5
)

print("\n" + "="*60)
print("TRAINING COMPLETE")
print("="*60)
print("\nModel saved to: models/movie_lora/")
print("\nTest it:")
print("  python run_pipeline.py 'epic battle' --lora --lora-path models/movie_lora")
