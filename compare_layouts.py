"""Compare LayoutGAN vs PosterO vs Templates"""
import time

print("=" * 70)
print("LAYOUT GENERATION COMPARISON")
print("=" * 70)

# 1. Legacy LayoutGAN (deprecated)
print("\n[1] LayoutGAN (DEPRECATED)")
print("-" * 70)
try:
    from src.layout_gan import LayoutGAN
    import torch
    
    start = time.time()
    gan = LayoutGAN()
    img_features = torch.randn(1, 512)
    text_features = torch.randn(1, 256)
    layout = gan.generate(img_features, text_features)
    elapsed = time.time() - start
    
    print(f"✓ Generated layout in {elapsed:.3f}s")
    print(f"  Shape: {layout.shape}")
    print(f"  Status: Works but OUTDATED (2018 architecture)")
except Exception as e:
    print(f"✗ Error: {e}")

# 2. PosterO (CVPR 2025)
print("\n[2] PosterO (CVPR 2025) - RECOMMENDED")
print("-" * 70)
try:
    from src.postero_adapter import PosterOAdapter
    from PIL import Image
    import numpy as np
    
    start = time.time()
    postero = PosterOAdapter(canvas_size=(720, 1080))
    dummy_image = Image.new('RGB', (720, 1080), (200, 200, 200))
    layout = postero.generate_layout(dummy_image, "cyberpunk neon city")
    template = postero.layout_to_template(layout)
    elapsed = time.time() - start
    
    print(f"✓ Generated layout in {elapsed:.3f}s")
    print(f"  Elements: {layout['cls_elem']}")
    print(f"  Bboxes: {len(layout['box_elem'])} regions")
    print(f"  Template layers: {len(template['layers'])}")
    print(f"  Status: STATE-OF-THE-ART (CVPR 2025)")
except Exception as e:
    print(f"✗ Error: {e}")

# 3. Template-based (current system)
print("\n[3] Template-based (Legacy)")
print("-" * 70)
try:
    import glob
    import json
    import random
    
    start = time.time()
    template_files = glob.glob("templates/template*_layers.json")
    if template_files:
        template_file = random.choice(template_files)
        with open(template_file) as f:
            template = json.load(f)
        elapsed = time.time() - start
        
        print(f"✓ Loaded template in {elapsed:.3f}s")
        print(f"  File: {template_file}")
        print(f"  Size: {template['size']}")
        print(f"  Layers: {len(template['layers'])}")
        print(f"  Status: SIMPLE but limited variety")
    else:
        print("✗ No templates found")
except Exception as e:
    print(f"✗ Error: {e}")

# Summary
print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("""
✅ USE PosterO: Modern, flexible, content-aware layouts
   - Best quality and variety
   - Adapts to image content
   - CVPR 2025 state-of-the-art

⚠️  Templates: Simple fallback
   - Fast but limited
   - Good for prototyping
   - No content awareness

❌ LayoutGAN: Deprecated
   - Outdated architecture
   - Requires training
   - Replaced by PosterO
""")

print("=" * 70)
print("To use PosterO in your pipeline:")
print("  pipeline = Key2PosterPipeline(use_postero=True)")
print("=" * 70)
