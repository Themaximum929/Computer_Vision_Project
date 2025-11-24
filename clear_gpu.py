"""Clear GPU memory"""
import torch
import gc

print("Clearing GPU memory...")
torch.cuda.empty_cache()
gc.collect()
print(f"GPU memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
print(f"GPU memory reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
print("✓ Done")
