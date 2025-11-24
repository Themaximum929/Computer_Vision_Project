"""Quick comparison: Old PIL vs New FLUX text rendering"""
import sys
from src.pipeline import Key2PosterPipeline
from pathlib import Path

Path("outputs/text_comparison").mkdir(parents=True, exist_ok=True)

keywords = "cyberpunk neon city"
method = sys.argv[1] if len(sys.argv) > 1 else "old"

if method == "old":
    print("\n" + "="*60)
    print("OLD METHOD: PIL Text Overlay")
    print("="*60)
    pipeline = Key2PosterPipeline(
        use_flux=True,
        add_title=True,
        genre_lora=True,
        modern_text=False,
        super_resolution=False
    )
    pipeline.generate_poster(keywords, "outputs/text_comparison/old_pil.png", seed=42)
    print("\n✅ Run: python test_text_comparison.py new")
else:
    print("\n" + "="*60)
    print("NEW METHOD: FLUX Diffusion Text")
    print("="*60)
    pipeline = Key2PosterPipeline(
        use_flux=True,
        add_title=True,
        genre_lora=True,
        modern_text=True,
        super_resolution=False
    )
    pipeline.generate_poster(keywords, "outputs/text_comparison/new_flux.png", seed=42)
    print("\n✅ DONE! Compare: outputs/text_comparison/")
