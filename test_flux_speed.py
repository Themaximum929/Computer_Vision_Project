"""Test FLUX speed with and without text embedding"""
import time
import torch
from src.pipeline import Key2PosterPipeline

print("=" * 60)
print("FLUX Speed Test: With vs Without Text Embedding")
print("=" * 60)

# Test with single pipeline, toggle text on/off
print("\nLoading FLUX pipeline...")
start = time.time()
pipeline = Key2PosterPipeline(
    use_flux=True,
    add_title=False,
    genre_lora=False,
    remove_text=False,
    super_resolution=False
)
load_time = time.time() - start
print(f"✓ Loaded in {load_time:.1f}s")

# Test 1: Without text
print("\n[TEST 1] Generation WITHOUT text embedding")
print("-" * 60)
pipeline.add_title = False
start = time.time()
image1, _, _ = pipeline.generate_poster("cyberpunk city", seed=42, evaluate=False)
time1 = time.time() - start
print(f"✓ Generated in {time1:.1f}s")

# Clear cache
torch.cuda.empty_cache() if torch.cuda.is_available() else None

# Test 2: With text
print("\n[TEST 2] Generation WITH text embedding")
print("-" * 60)
pipeline.add_title = True
if hasattr(pipeline, 'generator'):
    from src.enhanced_flux_text import StyleEnhancedFlux
    pipeline.flux_text_gen = StyleEnhancedFlux(shared_generator=pipeline.generator)
start = time.time()
image2, _, _ = pipeline.generate_poster("cyberpunk city", seed=42, evaluate=False)
time2 = time.time() - start
print(f"✓ Generated in {time2:.1f}s")

# Results
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Without text: {time1:.1f}s")
print(f"With text:    {time2:.1f}s")
print(f"Difference:   {abs(time2-time1):.1f}s ({'+' if time2>time1 else '-'}{abs(time2-time1)/time1*100:.1f}%)")
print("=" * 60)
