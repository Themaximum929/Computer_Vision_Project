"""Compare all 3 text rendering methods"""
from src.pipeline import Key2PosterPipeline
from src.flux_text_inpainting import FluxTextPrompt
from pathlib import Path

Path("outputs/comparison").mkdir(parents=True, exist_ok=True)

keywords = "cyberpunk neon city"
seed = 42

print("\n" + "="*60)
print("COMPARING 3 TEXT RENDERING METHODS")
print("="*60)

# Method 1: PIL Overlay (Old)
print("\n[1/3] Method 1: PIL Text Overlay")
print("-"*60)
pipeline1 = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=True,
    modern_text=False,
    super_resolution=False
)
pipeline1.generate_poster(keywords, "outputs/comparison/1_pil_overlay.png", seed=seed)
print("✓ PIL overlay complete")

# Clear GPU
import torch
torch.cuda.empty_cache()
del pipeline1

# Method 2: Modern PIL with Effects
print("\n[2/3] Method 2: Modern PIL with Glow/Shadow")
print("-"*60)
pipeline2 = Key2PosterPipeline(
    use_flux=True,
    add_title=True,
    genre_lora=True,
    modern_text=True,
    super_resolution=False
)
pipeline2.generate_poster(keywords, "outputs/comparison/2_modern_pil.png", seed=seed)
print("✓ Modern PIL complete")

# Clear GPU
torch.cuda.empty_cache()
del pipeline2

# Method 3: FLUX Text Generation
print("\n[3/3] Method 3: FLUX Text Generation")
print("-"*60)
generator = FluxTextPrompt()
image = generator.generate_with_text(
    base_prompt="cyberpunk neon city",
    title="NEON CITY",
    genre="scifi",
    seed=seed
)
image.save("outputs/comparison/3_flux_generated.png")
print("✓ FLUX generation complete")

print("\n" + "="*60)
print("✅ COMPARISON COMPLETE!")
print("="*60)
print("\nCheck outputs/comparison/ for results:")
print("  1_pil_overlay.png    - Basic PIL text")
print("  2_modern_pil.png     - PIL with glow effects")
print("  3_flux_generated.png - FLUX generated text")
print("\nExpected results:")
print("  Method 1: Clean but basic")
print("  Method 2: Professional with effects ⭐")
print("  Method 3: Unreliable text quality")
print("="*60)
