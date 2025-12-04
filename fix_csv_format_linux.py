"""Fix box_elem format in CSV files - Linux version"""
import pandas as pd
import ast
from pathlib import Path

pku_dir = Path.home() / "poster_dataset/pku"

for split in ['train', 'valid']:
    csv_path = pku_dir / f"annotation/{split}.csv"
    print(f"Fixing {csv_path}...")
    
    df = pd.read_csv(csv_path)
    
    # Fix box_elem format: convert list to proper format
    def fix_box(box_str):
        try:
            # Try to evaluate as-is
            box = ast.literal_eval(box_str)
            return str(box)
        except:
            # If it's a string like "[ 33 592 276 622]", convert to proper list
            box_str = box_str.strip()
            if box_str.startswith('[') and box_str.endswith(']'):
                # Remove brackets and split by spaces
                nums = box_str[1:-1].split()
                box = [int(n) for n in nums if n]
                return str(box)
            return box_str
    
    df['box_elem'] = df['box_elem'].apply(fix_box)
    df.to_csv(csv_path, index=False)
    print(f"✅ Fixed {len(df)} rows in {split}.csv")

print("\n✅ CSV files fixed!")