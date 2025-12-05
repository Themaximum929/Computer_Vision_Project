import pandas as pd

train_df = pd.read_csv('src/Dataset/pku/annotation/train_csv_9973.csv')
test_df = pd.read_csv('src/Dataset/pku/annotation/test_csv_905.csv')

print("Train CSV columns:", train_df.columns.tolist())
print("Test CSV columns:", test_df.columns.tolist())
print("\nTrain sample:")
print(train_df.head(3))
print("\nTest sample:")
print(test_df.head(3))

print("\nGrouping train by poster_path:")
for key, sub_df in train_df.groupby(by="poster_path"):
    print(f"Key: {key}, Split count: {len(key.split('/'))}")
    if len(key.split('/')) != 2:
        print(f"  BAD KEY: {key}")
    break

print("\nGrouping test by poster_path:")
for key, sub_df in test_df.groupby(by="poster_path"):
    split = "test"
    key_with_split = f"test/{key}" if split == "test" else key
    print(f"Original key: {key}, After adding split: {key_with_split}, Split count: {len(key_with_split.split('/'))}")
    if len(key_with_split.split('/')) != 2:
        print(f"  BAD KEY: {key_with_split}")
    break
