"""Check PKU dataset format"""
import pandas as pd
from pathlib import Path

pku_dir = Path("C:/Users/maxch/Downloads/Homeworks/poster_dataset/pku")
train_file = pku_dir / "data/train-00000-of-00015.parquet"

df = pd.read_parquet(train_file)
print("Columns:", df.columns.tolist())
print("\nFirst row:")
print(df.iloc[0])
print("\nDataFrame info:")
print(df.info())
