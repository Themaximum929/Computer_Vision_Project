"""Convert PKU dataset from HuggingFace Parquet to PosterO format"""

import pandas as pd
from pathlib import Path
from PIL import Image
import io
import shutil

# Paths
pku_dir = Path("C:/Users/maxch/Downloads/Homeworks/poster_dataset/pku")
data_dir = pku_dir / "data"
output_dir = pku_dir

# Create directories
(output_dir / "image/train/input").mkdir(parents=True, exist_ok=True)
(output_dir / "image/valid/input").mkdir(parents=True, exist_ok=True)
(output_dir / "annotation").mkdir(parents=True, exist_ok=True)

print("Converting PKU dataset...")

# Process train split
train_files = sorted(data_dir.glob("train-*.parquet"))
train_data = []

for i, file in enumerate(train_files):
    print(f"Processing {file.name}...")
    df = pd.read_parquet(file)
    
    for idx, row in df.iterrows():
        # Save image
        img = Image.open(io.BytesIO(row['inpainted_poster']['bytes']))
        img_name = f"train_{i:02d}_{idx:05d}.png"
        img.save(output_dir / "image/train/input" / img_name)
        
        # Collect annotations
        annotations = row['annotations']
        for ann_idx, poster_path in enumerate(annotations['poster_path']):
            train_data.append({
                'poster_path': img_name,
                'cls_elem': annotations['cls_elem'][ann_idx],
                'box_elem': str(annotations['box_elem'][ann_idx])  # Convert to string with commas
            })

# Use last 10% of train as valid
valid_split = int(len(train_data) * 0.9)
valid_data = train_data[valid_split:]
train_data = train_data[:valid_split]

# Copy images to valid folder
for item in valid_data:
    src = output_dir / "image/train/input" / item['poster_path']
    dst = output_dir / "image/valid/input" / item['poster_path'].replace('train_', 'valid_')
    if src.exists():
        shutil.copy(src, dst)
        item['poster_path'] = dst.name

pd.DataFrame(train_data).to_csv(output_dir / "annotation/train.csv", index=False)
pd.DataFrame(valid_data).to_csv(output_dir / "annotation/valid.csv", index=False)
print(f"✅ Saved {len(train_data)} train + {len(valid_data)} valid annotations")

print("\n✅ Dataset conversion complete!")
print(f"Images: {output_dir}/image/")
print(f"Annotations: {output_dir}/annotation/")
