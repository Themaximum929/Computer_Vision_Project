"""Simple test: Just compare text rendering methods"""
from src.pipeline import Key2PosterPipeline
from pathlib import Path

Path("outputs/text_comparison").mkdir(parents=True, exist_ok=True)

keywords = "cyberpunk neon city"

print("\n" + "="*60)
print("Testing OLD vs NEW Text Rendering")
print("="*60)

# Test with old PIL method
print("\n[1/2] OLD METHOD: PIL Text Overlay")
print("-"*60)
pipeline = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=True,
    modern_text=False,  # OLD: PIL
    super_resolution=False  # Faster
)
pipeline.generate_poster(keywords, "outputs/text_comparison/old_pil.png", seed=42)

# Clear GPU memory
import torch
torch.cuda.empty_cache()
del pipeline

print("\n\n[2/2] NEW METHOD: FLUX Diffusion Text")
print("-"*60)
pipeline = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=True,
    modern_text=True,  # NEW: FLUX diffusion
    super_resolution=False  # Faster
)
pipeline.generate_poster(keywords, "outputs/text_comparison/new_flux.png", seed=42)

print("\n" + "="*60)
print("✅ DONE! Compare images:")
print("  outputs/text_comparison/old_pil.png  (PIL)")
print("  outputs/text_comparison/new_flux.png (FLUX)")
print("="*60)
