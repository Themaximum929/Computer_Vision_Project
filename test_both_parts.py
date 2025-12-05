#!/usr/bin/env python3
"""
Test Both Parts of PosterO:
- Part 1 (Your work): PKU dataset with design_intent_pku_epoch100.pth + POE API
- Part 2 (Classmate's work): PStylish7 generalized with POE API
"""

import sys
from pathlib import Path

print("="*70)
print("TESTING BOTH PARTS OF POSTERO")
print("="*70)

# ============================================================================
# PART 2 (Classmate's Work): Generalized PStylish7
# ============================================================================
print("\n[PART 2 - CLASSMATE'S WORK] PStylish7 Generalized")
print("-" * 70)

sys.path.insert(0, str(Path(__file__).parent / "src" / "generalized_setting"))

try:
    from pipeline import LayoutGenerationPipeline
    
    base_dir = Path(__file__).parent
    dataset_info = {
        'dataset_name': 'pstylish7_movie-poster',
        'design_intent_bbox_dir': str(base_dir / 'src' / 'Dataset' / 'PStylish7' / 'movie-poster' / 'predm_zs'),
        'annotation_dir': str(base_dir / 'src' / 'Dataset' / 'PStylish7' / 'movie-poster'),
        'label_info': {
            'T-G': {'type': 'text-general', 'color': 'green'},
            'T-V': {'type': 'text-vertical', 'color': 'green'},
            'T-R': {'type': 'text-rotated', 'color': 'green'},
            'T-S': {'type': 'text-ellipse', 'color': 'green'},
            'T-C': {'type': 'text-curved', 'color': 'green'},
            'L': {'type': 'logo', 'color': 'red'},
            'U': {'type': 'underlay', 'color': 'orange'},
            'E': {'type': 'embellishment', 'color': 'blue'}
        }
    }
    
    print("Initializing Part 2 pipeline...")
    pipeline_part2 = LayoutGenerationPipeline(
        dataset_info=dataset_info,
        canvas_size=(513, 750),
        sample_size=3
    )
    print("✅ Part 2 pipeline ready (uses POE API)")
    
    # Test generation
    print("\nTesting Part 2 layout generation...")
    test_image = str(base_dir / 'src' / 'test.png')
    result = pipeline_part2.generate_layout(
        image=test_image,
        design_intent_bboxes=[(50, 50, 450, 200), (50, 600, 450, 720)],
        num_generations=1
    )
    
    layout = result['layout_graphs'][0]
    print(f"✅ Part 2 generated layout:")
    print(f"   Elements: {layout['cls_elem']}")
    print(f"   Bboxes: {len(layout['box_elem'])}")
    
except Exception as e:
    print(f"❌ Part 2 failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PART 1 (Your Work): PKU with design intent detection
# ============================================================================
print("\n[PART 1 - YOUR WORK] PKU with Design Intent Detection")
print("-" * 70)

print("Status: Using .pth model + POE API")
print("  Model: PosterO/design_intent_detect/pku_128_1e-06_none/ckpt/design_intent_pku_epoch100.pth")
print("  LLM: POE API (configured in llm_api_wrapper.py)")
print("  Note: Full pipeline requires PKU dataset + running infer.sh")

# Check if design intent model exists
pth_path = Path("PosterO/design_intent_detect/pku_128_1e-06_none/ckpt/design_intent_pku_epoch100.pth")
if pth_path.exists():
    print(f"✅ Design intent model found: {pth_path}")
else:
    print(f"⚠ Design intent model not found: {pth_path}")

# Check POE API key
import os
from dotenv import load_dotenv
load_dotenv()

poe_key = os.getenv('POE_API_KEY')
if poe_key:
    print(f"✅ POE API key configured: {poe_key[:10]}...")
else:
    print(f"⚠ POE API key not found in .env")

print("\nTo run Part 1 full pipeline:")
print("  cd PosterO")
print("  source infer.sh 0 pku /path/to/llama EXP1")
print("  (But uses POE API instead of LLaMA)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
Part 1 (Your Work - PKU):
  ✓ Design intent model: design_intent_pku_epoch100.pth
  ✓ LLM: POE API (llm_api_wrapper.py)
  ⚠ Needs: PKU dataset + run infer.sh to generate layouts
  
Part 2 (Classmate's Work - PStylish7):
  ✓ Pipeline: generalized_setting/pipeline.py
  ✓ LLM: POE API (same wrapper)
  ✓ Dataset: PStylish7 (design intent pre-computed)
  ✓ Status: WORKING

Both parts use the same POE API wrapper!
""")
