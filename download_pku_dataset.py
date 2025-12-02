"""Download PKU PosterLayout Dataset from HuggingFace"""

from huggingface_hub import snapshot_download
from pathlib import Path

# Download location
dataset_dir = Path("C:/Users/maxch/Downloads/Homeworks/poster_dataset/pku")
dataset_dir.mkdir(parents=True, exist_ok=True)

print("Downloading PKU PosterLayout dataset...")
print(f"Destination: {dataset_dir}")

snapshot_download(
    repo_id="creative-graphic-design/PKU-PosterLayout",
    repo_type="dataset",
    local_dir=str(dataset_dir)
)

print(f"\n✅ Dataset downloaded to: {dataset_dir}")
print("\nNext steps:")
print("1. Set DATASET_DIR environment variable")
print("2. Run: cd PosterO-CVPR2025/design_intent_detect")
print("3. Run: python preprocess.py --dataset pku")
print("4. Run: python main.py --mode train --dataset pku")
